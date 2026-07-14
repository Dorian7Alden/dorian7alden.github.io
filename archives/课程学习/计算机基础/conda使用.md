```
https://blog.csdn.net/chenxy_bwave/article/details/119996001
```





## 虚拟环境



- 查看有哪些虚拟环境

```
conda env list
```

- 激活虚拟环境

```
conda activate env_name
```

- 退出虚拟环境

```
conda deactivate
```

- 删除虚拟环境

```
conda remove --name env_name  package_name
conda remove --name env_name --all
```

- 使用conda创建虚拟环境的命令格式为:

```
conda create -n env_name python=3.8
```







## 源



- 查看当前下载源

```
conda config --show channels
```

- 添加镜像源

```
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free

  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/


conda config --set show_channel_urls yes
```

- 删除镜像源

```
conda config--remove channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
```

- 删除所有镜像源，恢复默认

```
conda config --remove-key channels
```































