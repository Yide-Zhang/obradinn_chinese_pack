# 奥伯拉丁的回归中文补丁包 （Return of the Obra Dinn Chinese patch）

这是玩家自制的《奥伯拉丁的回归》的中文补丁包。此补丁修改了游戏中的一些翻译（并相应地修改贴图），修改了游戏内的字体字形，并把对话改为双语。

This is a Chinese patch for *Return of the Obra Dinn* by a player. This patch alters some of translations in the game (meanwhile, changing the textures correspondingly), fixes the shape of glyghs of fonts used in the game, and makes the dialogues bilingual.

## 说明 (Notes)

**2025 年圣诞节游戏打折时会发布 v0.2.2 版本。** 该版本将修改部分翻译，重新支持 Windows 和 MacOS，并将推出使实况视频更容易过审的主播模式。

**Patch v0.2.2 will be release at Christmas 2025.** This upcoming version modifies some translations, supports both Windows and MacOS again and introduces a streamer mode that makes live video content easier to pass the review.

## 如何使用（How to use）

请前往 release 界面下载相应系统的补丁 v 0.2.1 版本的可执行文件（包括 Windows 和 MacOS），双击运行程序（MacOS 版需要在 `设置-隐私与安全性` 中设置补丁文件的访问权限）并按照 GUI 界面操作。若出现访问权限问题，可能需要用户手动输入（或者粘贴）游戏路径。正确的路径形式如下：

- Windows: `./ObraDinn/ObraDinn_Data/`

- MacOS: `./ObraDinn/ObraDinn.app/Contents/Resources/Data/`

如果以上方法安装失败，也可以使用如下的方法手动安装：下载**相应系统**的补丁文件包，解压缩后，

- 文本补丁：

    - 将 `lang-zh-s` 覆盖到上述路径下（下略）的 `./StreamingAssets/`；

    - 将 `Assembly-CSharp.dll` 覆盖到 `./Managed/`；

    - 将 `sharedaseets6.assets` 覆盖到 `./`。

- 字体补丁：

    - 将 `sharedassets0.assets` 覆盖到 `./`；

    - 将 `sharedassets2.assets` 覆盖到 `./`。

**建议备份原文件，以防止补丁出错。**

Please go to "Release" to download patch v 0.2.1 (executable file) for your operating system (Windows or MacOS). Double click the application (For MacOS, you need to set the accessibility authority of the patch in `Settings-Privacy&Security`) and operate as the GUI guides. You may have to type in (or paste) the path to the game files for lack of accessibility authority. A correct path should look like:

- Windows: `./ObraDinn/ObraDinn_Data/`

- MacOS: `./ObraDinn/ObraDinn.app/Contents/Resources/Data/`

If you cannot install patch as the method above, you can also manually install it by this method: Download the patch file pack **for your operating system**, decompress the zip, then

- Text:

    - Copy `lang-zh-s` to `./StreamingAssets/` in the directions mentioned above (left out below);

    - Copy `Assembly-CSharp.dll` to `./Managed/`;

    - Copy `sharedassets6.assets` to `./`.

- Font:

    - Copy `sharedassets0.assets` to `./`;

    - Copy `sharedassets2.assets` to `./`.

**You are suggested to back up the original files to avoid any errors triggered by the patch.**

## 已经知道的缺点（Disadvantages already found）

尚未发现。如果您遇到问题，请提交 issue。

Temporarily not found. If you find a problem, please submit an issue.

## 鸣谢（Acknowledgements）

感谢在 v 0.1.0 补丁的宣传视频下悉心指正错误并和我讨论的所有观众。

感谢 [@二元三次单项式](https://b23.tv/qHi5w0G) 的私信交流。

感谢 [@Orion_stel](https://b23.tv/ZtRoBC5) 的建议和私信交流. 

感谢 [@蹦跶不喜欢摄像头](https://b23.tv/AbwrGvh) 测试 MacOS 版本的补丁。

Thanks to all audiences who corrects the translations and discusses with me in the comments of AD video for v 0.1.0 patch.

Thanks to [@二元三次单项式](https://b23.tv/qHi5w0G) who messages me to discuss the details.

Thanks to [@Orion_stel](https://b23.tv/ZtRoBC5) who gives suggestion and communicates with me to discuss the details.

Thanks to [@蹦跶不喜欢摄像头](https://b23.tv/AbwrGvh) for testing MacOS patch.

## AI 生成内容（AI generated content）

本补丁使用 AI 生成代码。

This patch uses AI to generate codes.
