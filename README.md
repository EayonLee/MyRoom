# MyRoom

一个基于 Three.js 的实时 3D 房间展示器。项目将 Blender 制作的房间模型导出为 GLB，并在浏览器中提供预设机位、自由查看、灯光和基础性能信息。

在线仓库：[EayonLee/MyRoom](https://github.com/EayonLee/MyRoom)

## 功能

- 使用 Three.js 加载并渲染 `public/assets/room.glb`。
- 提供主桌、电脑角、侧面三个预设机位，并带有平滑转场。
- 支持自由查看模式：拖动旋转、滚轮缩放。
- 使用阴影、雾效、色调映射和多光源还原室内氛围。
- 页面显示模型三角面数量和实时 FPS，便于观察场景性能。
- Blender 脚本可重新生成房间模型和离线渲染图。

## 技术栈

- [Vite](https://vite.dev/)：开发服务器和生产构建
- [TypeScript](https://www.typescriptlang.org/)：类型安全的前端代码
- [Three.js](https://threejs.org/)：WebGL 3D 渲染
- [Blender](https://www.blender.org/)：房间建模、材质和 GLB 导出（可选）

## 环境要求

- Node.js 22 或更高版本（建议使用当前 Node.js LTS）
- npm 10 或更高版本
- 只有在需要重新生成模型时才需要安装 Blender，并确保命令行中可以直接调用 `Blender`

## 本地运行

```bash
npm install
npm run dev
```

开发服务器默认监听 `http://127.0.0.1:9100`。打开地址后，可以通过以下方式操作：

| 操作 | 功能 |
| --- | --- |
| 点击“主桌 / 电脑角 / 侧面” | 切换预设机位 |
| `1` / `2` / `3` | 切换对应预设机位 |
| `F` | 进入或退出自由查看 |
| `Esc` | 返回主桌机位 |
| 自由查看模式下拖动 | 旋转镜头 |
| 自由查看模式下滚轮 | 缩放镜头 |

## 构建与预览

构建命令会先执行 TypeScript 类型检查，然后生成 Vite 生产文件：

```bash
npm run build
npm run preview
```

生产预览默认监听 `http://127.0.0.1:9101`。构建产物位于 `dist/`，该目录是本地生成目录，不提交到仓库。

## 重新生成 Blender 资产

仓库中已保留可直接运行的模型资产 `public/assets/room.glb`，普通前端开发不需要安装 Blender。需要修改房间模型时，可执行：

```bash
npm run room
```

该脚本调用 `blender/props/room.py`，读取 `build/room.blend`，将模型输出到 `public/assets/room.glb`，并把离线预览图输出到 `build/room.png`。`build/` 和 Python 缓存均被 Git 忽略；更新后的 `public/assets/room.glb` 需要按改动一起提交。

## 项目结构

```text
.
├── blender/              # Blender 建模、材质和导出脚本
├── public/assets/        # 浏览器直接使用的静态资源（包含 room.glb）
├── src/main.ts           # Three.js 场景、镜头和交互逻辑
├── src/style.css         # 页面 HUD 和控件样式
├── tools/                # 辅助开发脚本
├── index.html            # 应用入口 HTML
├── package.json          # npm 脚本和依赖
└── vite.config.*         # 如后续增加 Vite 配置，放在此处
```

## 参与贡献

主分支用于保持可构建、可 review 的稳定状态。建议按开源项目常用流程参与：

1. Fork 本仓库。
2. 从 `main` 创建一个描述清晰的分支。
3. 完成修改，并在本地运行 `npm run build`。
4. 将分支推送到自己的 Fork，提交 Pull Request 到本仓库的 `main`。
5. 在 PR 中说明修改内容、测试方式，以及是否更新了 Blender/GLB 资产。

请尽量保持提交聚焦，避免提交 `node_modules/`、`dist/`、`build/`、本机配置或工具缓存。提交代码前可以运行：

```bash
git diff --check
npm run build
```

Bug 或功能建议请使用 GitHub Issues；涉及安全问题时，请不要在公开 Issue 中发布敏感细节。

## 许可证

当前项目元数据中的许可证为 `ISC`。如需发布稳定的开源版本，建议在仓库根目录补充与该声明一致的 `LICENSE` 文件。

