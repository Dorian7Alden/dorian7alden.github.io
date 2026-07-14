vscode 插件



https://zhuanlan.zhihu.com/p/112016680





背景图片配置

```
{
  // ... 你其他的 VSCode 设置（如字体、主题等） ...

  // 1. 总开关：开启背景功能
  "background.enabled": true,

  // 2. 全屏背景配置（覆盖整个 VSCode 窗口）
  "background.fullscreen": {
    "images": [
      "file:///home/dorian/Pictures/wallpaper/【哲风壁纸】动漫壁纸-动漫风景.png"
    ],
    "opacity": 0.15,        // 透明度自己调节
    "size": "cover",        // 铺满且不变形
    "position": "center",   // 居中
    "interval": 0,
    "random": false
  }

  // ... 你其他的设置 ...
}
```

