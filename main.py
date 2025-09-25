import sys, re
from pathlib import Path
import shutil


# ==============================
# 自动获取 Steam 游戏目录
# ==============================
def get_steam_game_path():
    """
    查找固定 Steam AppID=653530 的安装目录。
    返回: (success: bool, path: Optional[str])
    """
    # ------- 内部工具：候选 Steam 根目录 -------
    def _candidate_steam_roots():
        roots = []
        home = Path.home()
        if sys.platform.startswith("win"):
            roots += [Path("C:/Program Files (x86)/Steam"),
                      Path("C:/Program Files/Steam")]
            try:
                import winreg  # type: ignore
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                    val, _ = winreg.QueryValueEx(k, "SteamPath")
                    if val:
                        roots.append(Path(val))
            except Exception:
                pass
        elif sys.platform == "darwin":
            roots += [
                home / "Library/Application Support/Steam",
                home / "Library/Application Support/Steam/steamapps/..",
            ]
        else:
            roots += [
                home / ".local/share/Steam",
                home / ".steam/steam",
                home / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
            ]
        seen, uniq = set(), []
        for p in roots:
            try:
                p = p.resolve()
            except Exception:
                continue
            if p.exists() and p not in seen:
                uniq.append(p)
                seen.add(p)
        return uniq

    # ------- 内部工具：解析 Valve KeyValues (.vdf/.acf) -------
    _tok = re.compile(r'"((?:\\.|[^"\\])*)"|(\{)|(\})')

    def _parse_keyvalues(text: str):
        tokens = []
        for m in _tok.finditer(text):
            if m.group(1) is not None:
                tokens.append(("S", m.group(1)))
            elif m.group(2) is not None:
                tokens.append(("{", "{"))
            elif m.group(3) is not None:
                tokens.append(("}", "}"))
        i = 0

        def obj():
            nonlocal i
            d = {}
            while i < len(tokens):
                t, v = tokens[i]
                if t == "}":
                    i += 1
                    break
                if t != "S":
                    i += 1
                    continue
                key = v
                i += 1
                if i < len(tokens) and tokens[i][0] == "{":
                    i += 1
                    d[key] = obj()
                elif i < len(tokens) and tokens[i][0] == "S":
                    d[key] = tokens[i][1]
                    i += 1
                else:
                    d[key] = ""
            return d

        if not tokens:
            return {}
        if tokens[0][0] == "S" and len(tokens) > 1 and tokens[1][0] == "{":
            i = 2
            return {tokens[0][1]: obj()}
        if tokens[0][0] == "{":
            i = 1
            return obj()
        return {}

    def _load_vdf(path: Path):
        for enc in ("utf-8", "utf-16", "utf-8-sig"):
            try:
                return _parse_keyvalues(path.read_text(encoding=enc, errors="ignore"))
            except Exception:
                continue
        return _parse_keyvalues(path.read_text(errors="ignore"))

    def _library_paths(steam_root: Path):
        steamapps = steam_root / "steamapps"
        libs = []
        vdf = steamapps / "libraryfolders.vdf"
        if vdf.exists():
            data = _load_vdf(vdf)
            entries = data.get("libraryfolders", data)
            if isinstance(entries, dict):
                for _, v in entries.items():
                    p = None
                    if isinstance(v, dict) and "path" in v:
                        p = Path(v["path"])
                    elif isinstance(v, str):
                        p = Path(v)
                    if p and (p / "steamapps").exists():
                        libs.append(p)
        if steamapps.exists():
            base = [steam_root]
            libs = base + [p.resolve() for p in libs if p.resolve() != steam_root.resolve()]
        else:
            libs = [steam_root]
        return libs

    APPID = "653530"
    for root in _candidate_steam_roots():
        for lib in _library_paths(root):
            manifest = lib / "steamapps" / f"appmanifest_{APPID}.acf"
            if manifest.exists():
                data = _load_vdf(manifest)
                app = data.get("AppState", data)
                installdir = str(app.get("installdir", "")).strip()
                if installdir:
                    path = (lib / "steamapps" / "common" / installdir).resolve()
                    return True, str(path)
    return False, None


# ==============================
# 用户目录优先
# ==============================
def get_game_data_path(custom_path: str | None = None):
    """
    获取游戏数据目录：
    - 如果用户提供 custom_path，则优先使用
    - 否则走 Steam 自动查找
    """
    if custom_path:
        p = Path(custom_path).expanduser().resolve()
        if p.exists():
            return True, str(p)
        return False, None
    return get_steam_game_data_path()


def get_steam_game_data_path():
    ok, base_path = get_steam_game_path()
    if not ok or not base_path:
        return False, None

    base = Path(base_path)
    if sys.platform.startswith("win"):
        return True, str(base / "ObraDinn_Data")
    elif sys.platform == "darwin":
        return True, str(base / "ObraDinn.app" / "Contents" / "Resources" / "Data")
    else:
        return True, str(base / "ObraDinn_Data")


# ==============================
# 文件检查/备份/补丁
# ==============================
def check_obra_dinn_files(custom_path: str | None = None) -> bool:
    ok, datapath = get_game_data_path(custom_path)
    if not ok or not datapath:
        return False
    base = Path(datapath)
    required_files = [
        base / "StreamingAssets" / "lang-zh-s",
        base / "sharedassets0.assets",
        base / "sharedassets2.assets",
        base / "sharedassets6.assets",
        base / "Managed" / "Assembly-CSharp.dll",
    ]
    return all(f.exists() for f in required_files)


def backup_obra_dinn_files(backup_dir: str, custom_path: str | None = None) -> bool:
    ok, datapath = get_game_data_path(custom_path)
    if not ok or not datapath:
        return False
    base = Path(datapath)
    backup_dir = Path(backup_dir).expanduser().resolve()
    required_files = [
        Path("StreamingAssets/lang-zh-s"),
        Path("sharedassets0.assets"),
        Path("sharedassets2.assets"),
        Path("sharedassets6.assets"),
        Path("Managed/Assembly-CSharp.dll"),
    ]
    all_ok = True
    for rel in required_files:
        src = base / rel
        if not src.exists():
            print(f"[警告] 缺少源文件: {src}")
            all_ok = False
            continue
        dest = backup_dir / rel
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            print(f"已备份: {src} -> {dest}")
        except Exception as e:
            print(f"[错误] 复制 {src} 失败: {e}")
            all_ok = False
    return all_ok


def resource_path(rel: str) -> Path:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / rel
    return Path(__file__).parent / rel


def patch_obra_dinn_files(text: bool, font: bool, custom_path: str | None = None) -> bool:
    ok, datapath = get_game_data_path(custom_path)
    if not ok or not datapath:
        print("[错误] 未找到游戏数据目录")
        return False
    base = Path(datapath)
    patches_dir = resource_path("patches")
    if not patches_dir.exists():
        print(f"[error] Patch directory does not exist: {patches_dir}")
        return False

    text_files = {
        "lang-zh-s": base / "StreamingAssets" / "lang-zh-s",
        "sharedassets6.assets": base / "sharedassets6.assets",
        "Assembly-CSharp.dll": base / "Managed" / "Assembly-CSharp.dll",
    }
    font_files = {
        "sharedassets0.assets": base / "sharedassets0.assets",
        "sharedassets2.assets": base / "sharedassets2.assets",
    }

    selected = {}
    if text: selected.update(text_files)
    if font: selected.update(font_files)

    if not selected:
        print("[info] No patching operation chosen.")
        return True

    all_ok = True
    for patch_name, target in selected.items():
        src = patches_dir / patch_name
        if not src.exists():
            print(f"[warning] Patch file does not exist: {src}")
            all_ok = False
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, target)
            print(f"Replaced: {target}")
        except Exception as e:
            print(f"[error] Failed to replace {target}: {e}")
            all_ok = False
    return all_ok
