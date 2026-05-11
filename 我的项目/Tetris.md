# C语言俄罗斯方块开发日志

## 11.27

### 准备工作

>在电子书《深入体验C语言项目开发》中看到俄罗斯方块的开发，受到启发，想要挑战自己开发俄罗斯方块小游戏。
>
>了解到一个图形库“easyx.h”，计划借助此库完成开发。
>
>下载并安装好库之后，简单了解了一下easyx这个库的功能。
>
>尝试了基础的简单画图.
>
>## 

 

## 11.28

### 获取按键操作

>在我使用_getch()函数模拟获取按键的过程中，发现一个巨大的问题：
>
>绘图的界面和控制台不是同一个窗口，我只能在控制台获取按键，因此，我在获取按键之前，必须先让鼠标聚焦在控制台上，不能隐藏掉控制台界面，只显示绘画的图形界面，相当的不优雅。
>
>在B站上观摩他人实现俄罗斯方块的过程，发现，可以使用easyx库中自带的ExMessage完成获取按键的过程。
>
>根据示例代码，初次尝试，无法正常获取键盘输入，但是鼠标操作正常，不知道原因，重新观看B站视频教程的实现过程。
>
>发现问题，问题原因：消息类型判错错误。
>
>```c
>ExMessage key;
>while (1)
>{
>        key = getmessage(EX_KEY);
>        switch(key.vkcode)	// 消息类型应为 vkcode(virtual keyboard)，示例为 message误认为是全局消息，
>        {
>            ...
>        }
>}
>```
>
>重新学习easyx库相关内容
>
>解决了按键点一次运行执行多次的问题，自认为前期工作准备完成，能够绘图，能够获取按键信息，接下来就是游戏思路的设计以及代码的实现。
>
>完成了绘画游戏界面

## 11.29

### 遇到问题

>怎么旋转方块
>
>不同的文件之中怎么共享变量
>
>二维数组的相关操作不熟悉

## 12.13

从头开始。

### 流程分析

绘制流程图

![image-20241213015509454](C:\Users\Senior ShuangYao\AppData\Roaming\Typora\typora-user-images\image-20241213015509454.png)

相关代码分析：

数据结构：

int x=10，int y=18	游戏格数

int map[x]\[y]	二维坐标地图		

int curBlock[4]\[4]	当前方块数据

int nextBlock[4]\[4]	下一个方块数据			

int blocks[7]\[4]\[4]	所有方块初始数据

int blockID	方块种类判断[0-6]		

int curPos[x]\[y]	当前方块的坐标

int speed	游戏刷新间隔|方块下落速度

函数分析：

void draw_gui(void)	绘画gui

​	void draw_game_area(void)	绘画游戏区域

​	void draw_next_area(void)	  绘画下一个方块区域

​	void draw_info_area(void)	   绘画游戏信息区域

void draw_block(int** curBlock, int** curPos)	绘画新坐标下的方块

void clean_block(int** preBlock, int** prePos)	清除旧坐标下的方块

void game_ing(void)	游戏算法实现

​	int** block_generate(void)	生成一个新方块(给一个随机数，改变方块的初始方向)，返回方块数据curBlock

​	int** block_falling(void)	方块下落，返回坐标curPos

​	int** block_change_shape(int** curBlock)	改变方块样式，返回方块数据curBlock

​	bool block_check_barrier(int** curPos)	检查是否碰壁，返回bool

​	void block_clean_line(void)	清除满行



## 2025.2.4

> 再再战俄罗斯方块

计划:

1. 更改底层代码,C语言转C++.因此浏览一遍C++文档.面向对象内容加上一些常用的库.顺便复习编程语言
2. 重新学习easyx绘图库.
3. 一个一个小环节的写,调试.先让一部分跑起来,再丰富内容.



### 第一步：让单方块动起来

```c++
#include <iostream>
#include <easyx.h>
#include <graphics.h>
using namespace std;

int main()
{
	initgraph(400, 700);

	for (int i = 1; i <= 10; i++)
	{
		clearrectangle(10, (i - 1) * 20, 30, i * 20);
		fillrectangle(10, i * 20, 30, (i + 1) * 20);
		Sleep(1000);
	}

	system("pause");
	return 0;
}
```

### 第二步：让完整方块动起来

```c++
#include <iostream>
#include <easyx.h>
#include <graphics.h>
using namespace std;

const int BLOCK_SIZE = 30;   // 一个方块的边长大小
const int X = 10;			 // 横向方块数量
const int Y = 18;			 // 纵向方块数量
const int BLOCK_TYPES = 20;  // 不同方块类型的个数 

class Tetris
{
	public:
		int block_id = 2;
		int block_total_type = 20;
		int block_data[BLOCK_TYPES][16] = {
			// 仅仅给出三个作为示例，后面再补充方块
			{
				0, 0, 0, 0,
				0, 1, 1, 0,
				0, 1, 1, 0,
				0, 0, 0, 0
			}, 
			{
				0, 0, 0, 0,
				1, 1, 1, 1,
				0, 0, 0, 0,
				0, 0, 0, 0
			},
			{
				0, 1, 0, 0,
				0, 1, 0, 0,
				0, 1, 0, 0,
				0, 1, 0, 0
			}
		};
		int map[X][Y] = { 0 };  // 地图方块数据，0: 未被占用， 1: 被占用
		int block_pos[2] = { 0 };  // 4*4方块在地图中的坐标 [0]: x  ... [1]: y 
		
		void init(void);
		void set_block_pos_to_start(int block_id, int* block_pos);
		void block_down(int block_id, int* block_pos);
};

int main()
{
	Tetris game;
	game.init();
	game.set_block_pos_to_start(game.block_id, game.block_pos);


	while (true)
	{
		game.block_down(game.block_id, game.block_pos);
		Sleep(1000);
	}
	
	Sleep(4000);
	return 0;
}

// 初始化游戏界面
void Tetris::init(void)
{
	// 初始化桌布大小
	initgraph((X + 2) * BLOCK_SIZE, (Y + 1) * BLOCK_SIZE);

	// 画边界障碍
	setfillcolor(RGB(56, 56, 56));  // 设置边界为灰色
	POINT pts_barrier[] = { {0.5 * BLOCK_SIZE,0}, {BLOCK_SIZE, 0},
							{BLOCK_SIZE, Y * BLOCK_SIZE}, {(X + 1) * BLOCK_SIZE,Y * BLOCK_SIZE},
							{(X + 1) * BLOCK_SIZE,0}, {(X + 1.5) * BLOCK_SIZE,0},
							{(X + 1.5) * BLOCK_SIZE,(Y + 0.5) * BLOCK_SIZE}, {0.5 * BLOCK_SIZE,(Y + 0.5) * BLOCK_SIZE} };
	fillpolygon(pts_barrier, 8);  // 起点开始8个顺时针顶点坐标 (x, y) 
}

// 刷新方块的时候，获取方块的起始位置，使下一刻就能显示出方块
void Tetris::set_block_pos_to_start(int block_id, int* block_pos)
{
	block_pos[0] = 3;
	block_pos[1] = -4;
	bool is_block = false;
	for (int row = 3; row >= 0; row--)
	{
		if (is_block)
		{
			break;
		}
		for (int col = 0; col <= 3; col++)
		{
			if (block_data[block_id][row * 4 + col] == 1)
			{
				if (is_block)
				{
					break;
				}
				block_pos[1] += (3 - row);
				is_block = true;
			}
		}
	}
}

void Tetris::block_down(int block_id, int* block_pos)
{
	setorigin(BLOCK_SIZE, 0);
	for (int row = 0; row < 4; row++)
	{
		for (int col = 0; col < 4; col++)
		{
			if (block_data[block_id][row * 4 + col] == 1)
			{
				clearrectangle((block_pos[0] + col) * BLOCK_SIZE,
					(block_pos[1] + row) * BLOCK_SIZE,
					(block_pos[0] + col + 1) * BLOCK_SIZE,
					(block_pos[1] + row + 1) * BLOCK_SIZE);
			}
		}
	}

	block_pos[1]++;

	for (int row = 0; row < 4; row++)
	{
		for (int col = 0; col < 4; col++)
		{
			if (block_data[block_id][row * 4 + col] == 1)
			{
				fillrectangle((block_pos[0] + col) * BLOCK_SIZE,
					(block_pos[1] + row) * BLOCK_SIZE,
					(block_pos[0] + col + 1) * BLOCK_SIZE,
					(block_pos[1] + row + 1) * BLOCK_SIZE);
			}
		}
	}
}
```

## 2.5

### 第三步：让多个方块堆叠起来

```c++
#include <iostream>
#include <easyx.h>
#include <graphics.h>
using namespace std;

const int BLOCK_SIZE = 30;   // 一个方块的边长大小
const int X = 10;			 // 横向方块数量
const int Y = 18;			 // 纵向方块数量
const int BLOCK_TYPES = 20;  // 不同方块类型的个数 共19种

int speed = 100;


class Tetris
{
	public:
		int block_id = rand() % 19;
		int block_total_type = 20;
		int block_data[BLOCK_TYPES][16] = {
			// 仅仅给出三个作为示例，后面再补充方块
			{  // 1
				0, 0, 0, 0,
				0, 1, 1, 0,
				0, 1, 1, 0,
				0, 0, 0, 0
			}, 
			{  // 2
				0, 0, 0, 0,
				1, 1, 1, 1,
				0, 0, 0, 0,
				0, 0, 0, 0
			},
			{  // 3
				0, 1, 0, 0,
				0, 1, 0, 0,
				0, 1, 0, 0,
				0, 1, 0, 0
			},
			{  // 4
				0, 0, 0, 0,
				0, 1, 0, 0,
				1, 1, 1, 0,
				0, 0, 0, 0
			},
			{  // 5
				0, 0, 0, 0,
				0, 1, 0, 0,
				0, 1, 1, 0,
				0, 1, 0, 0
			},
			{  // 6
				0, 0, 0, 0,
				0, 0, 0, 0,
				1, 1, 1, 0,
				0, 1, 0, 0
			},
			{  // 7
				0, 0, 0, 0,
				0, 1, 0, 0,
				1, 1, 0, 0,
				0, 1, 0, 0
			},
			{  // 8
				0, 0, 0, 0,
				0, 0, 0, 0,
				0, 1, 1, 0,
				1, 1, 0, 0
			},
			{  // 9
				0, 0, 0, 0,
				1, 0, 0, 0,
				1, 1, 0, 0,
				0, 1, 0, 0
			},
			{  // 10
				0, 0, 0, 0,
				0, 0, 0, 0,
				1, 1, 0, 0,
				0, 1, 1, 0
			},
			{  // 11
				0, 0, 0, 0,
				0, 1, 0, 0,
				1, 1, 0, 0,
				1, 0, 0, 0
			},
			{  // 12
				0, 0, 0, 0,
				0, 1, 0, 0,
				0, 1, 1, 1,
				0, 0, 0, 0
			},
			{  // 13
				0, 0, 0, 0,
				0, 1, 1, 0,
				0, 1, 0, 0,
				0, 1, 0, 0
			},
			{  // 14
				0, 0, 0, 0,
				0, 1, 1, 1,
				0, 0, 0, 1,
				0, 0, 0, 0
			},
			{  // 15
				0, 0, 0, 0,
				0, 0, 1, 0,
				0, 0, 1, 0,
				0, 1, 1, 0
			},
			{  // 16
				0, 0, 0, 0,
				0, 0, 0, 1,
				0, 1, 1, 1,
				0, 0, 0, 0
			},
			{  // 17
				0, 0, 0, 0,
				0, 0, 1, 0,
				0, 0, 1, 0,
				0, 0, 1, 1
			},
			{  // 18
				0, 0, 0, 0,
				0, 1, 1, 1,
				0, 1, 0, 0,
				0, 0, 0, 0
			},
			{  // 19
				0, 0, 0, 0,
				0, 0, 1, 1,
				0, 0, 0, 1,
				0, 0, 0, 1
			}
		};
		int map[X][Y] = { 0 };  // 地图方块数据，0: 未被占用， 1: 被占用
		int block_pos[2] = { 0 };  // 4*4方块在地图中的坐标 [0]: x  ... [1]: y 
		
		void init(void);
		void set_block_pos_to_start(void);
		void block_down(void);
		void update_map(void);
		bool is_stop(void);
		bool is_end_game(void);
		int get_random_block(void);
};

int main()
{
	srand(time(0));
	Tetris game;
	game.init();

	game.block_id = game.get_random_block();
	game.set_block_pos_to_start();

	while (!game.is_end_game())
	{
		while (!game.is_stop())
		{
			game.block_down();
			Sleep(speed);
		}
		// 地图上更新方块数据
		game.update_map();
		// 新一轮
		game.block_id = game.get_random_block();
		game.set_block_pos_to_start();
		Sleep(speed);
	}

	cout << "!!!!!!!!!!!!!!!!!!!!!!!" << endl << "Game ends! 3s later auto close!" << endl;
	Sleep(3000);
	return 0;
}

// 初始化游戏界面
void Tetris::init(void)
{
	// 初始化桌布大小
	initgraph((X + 2) * BLOCK_SIZE, (Y + 1) * BLOCK_SIZE, EX_SHOWCONSOLE);

	// 画边界障碍
	setfillcolor(RGB(56, 56, 56));  // 设置边界为灰色
	POINT pts_barrier[] = { {0.5 * BLOCK_SIZE,0}, {BLOCK_SIZE, 0},
							{BLOCK_SIZE, Y * BLOCK_SIZE}, {(X + 1) * BLOCK_SIZE,Y * BLOCK_SIZE},
							{(X + 1) * BLOCK_SIZE,0}, {(X + 1.5) * BLOCK_SIZE,0},
							{(X + 1.5) * BLOCK_SIZE,(Y + 0.5) * BLOCK_SIZE}, {0.5 * BLOCK_SIZE,(Y + 0.5) * BLOCK_SIZE} };
	fillpolygon(pts_barrier, 8);  // 起点开始8个顺时针顶点坐标 (x, y) 
	cout << "Initialized game successfully!" << endl;
}

// 刷新方块的时候，获取方块的起始位置，使下一刻就能显示出方块
void Tetris::set_block_pos_to_start(void)
{
	// 初始化起点
	this->block_pos[0] = 3;
	this->block_pos[1] = -4;
	// 往下微调Y坐标
	bool is_block = false;
	for (int row = 3, col = 0; row >= 0; col++)
	{
		if (is_block)
		{
			break;
		}
		if (col >= 4)
		{
			row--;
			col = 0;
		}
		// 获取最底层实体方块的Y轴
		if (1 == this->block_data[this->block_id][row * 4 + col])
		{
			this->block_pos[1] += 3 - row;  // 往下移动的格数[0, 3]使下一刻就能显示出方块
			is_block = true;
			printf("Block_id: %d\tis setted to start spot!\tPos: [%d, %d]\n", 
				this->block_id, this->block_pos[0], this->block_pos[1]);
		}
	}
}

// 方块下落一格
void Tetris::block_down(void)
{
	setorigin(BLOCK_SIZE, 0);  // 设置 原点O 的位置
	for (int row = 3, col = 0; row >= 0; col++)  // 从下往上绘画
	{
		if (col >= 4)
		{
			row--;
			col = 0;
		}
		if (row < 0)
		{
			break;
		}
		if (1 == this->block_data[this->block_id][row * 4 + col])
		{
			// 清除当前位置的方块
			clearrectangle((this->block_pos[0] + col) * BLOCK_SIZE,
				(this->block_pos[1] + row) * BLOCK_SIZE,
				(this->block_pos[0] + col + 1) * BLOCK_SIZE,
				(this->block_pos[1] + row + 1) * BLOCK_SIZE);
			// 绘画下面位置的方块
			fillrectangle((this->block_pos[0] + col) * BLOCK_SIZE,
				(this->block_pos[1] + row + 1) * BLOCK_SIZE,
				(this->block_pos[0] + col + 1) * BLOCK_SIZE,
				(this->block_pos[1] + row + 2) * BLOCK_SIZE);
		}
	}
	this->block_pos[1]++;
	printf("Block_id: %d\tis downing!\tPos: [%d, %d]\n",
		this->block_id, this->block_pos[0], this->block_pos[1]);
}

// 更新地图方块数据，方块停止运动后占用地图
void Tetris::update_map(void)
{
	for (int row = 3, col = 0; row >= 0; col++)
	{
		if (col >= 4)
		{
			col = 0;
			row--;
		}
		if (row < 0)
		{
			break;
		}
		this->map[this->block_pos[0] + col][this->block_pos[1] + row] += this->block_data[this->block_id][row * 4 + col];
	}
}

// 方块是否停止运动（到达最底层，碰到其他方块）
bool Tetris::is_stop(void)
{
	for (int row = 3, col = 0; row >= 0; col++)
	{
		if (col >= 4)
		{
			col = 0;
			row--;
		}  
		// 最后一个循环为 row=-1, col=0 依旧会执行会出bug
		if (row < 0)
		{
			return false;
		}
		// 遍历到实体方块
		if (1 == this->block_data[this->block_id][row * 4 + col])
		{
			// 方块到达最底层
			if (Y - 1 <= this->block_pos[1] + row)
			{  // 坐标是从0开始计数，同数组，当为 Y-1
				printf("Block_id: %d\tarrived at the buttom!\tPos: [%d, %d]\n",
					this->block_id, this->block_pos[0], this->block_pos[1]);
				return true;
			}
			// 方块下面碰到其他方块
			if (1 == this->map[this->block_pos[0] + col][this->block_pos[1] + row + 1])
			{
				printf("Block_id: %d\thits another block!\tPos: [%d, %d]\n",
					this->block_id, this->block_pos[0], this->block_pos[1]);
				return true;
			}
		}
	}
}

// 是否结束游戏，方块堆满了
bool Tetris::is_end_game(void)
{
	for (int row = 3, col = 0; row >= 0; col++)
	{
		if (col >= 4)
		{
			col = 0;
			row--;
		}
		if (row < 0)
		{
			return false;
		}
		if (1 == this->map[this->block_pos[0] + col][0] && -1 == this->block_pos[1] + row)
		{  // 第0层对应的方块被占用即结束
			return true;
		}
	}
}

// 随机生成方块ID用于随机方块
int Tetris::get_random_block(void)
{
	return rand() % 19;
}
```

### 问题：一刻方块只能移动一次，不能一次移动两下，Sleep时间太长了，无法同时处理间隔内有两次移动。每下降一格才能平移一格，最大平移距离与最大垂直距离成正比。
​	  

## 2.27

正式版1.0

```
#include <iostream>
#include <easyx.h>
#include <time.h>
using namespace std;

#define X first
#define Y second

class Tetris
{
public:
	Tetris(int blocksX, int blocksY, int blockSize)
	{
		block.blocksX = blocksX;
		block.blocksY = blocksY;
		block.size = blockSize;
		UpdateBlockData();
	
		render.blockSpace = blockSize / 11;
		render.barrierPadding = blockSize * 2 / 7;
		render.barrierEllipse = 10;
		render.windowPadding = blockSize * 3 / 5;
		UpdateDrawLength();
	}

	IMAGE picBlocks[7];
	int colorId = 0;
	int map[20][20];
	int FPS = 1000 / 60;
	int cntFPS = 0;
	clock_t startTime;
	clock_t endTime;
	clock_t costTime;

	struct Render
	{
		pair<int, int> blockStart;
		int blockSpace;

		int windowPadding;
		int windowWidth;
		int windowHeight;

		int barrierPadding;
		int barrierWidth;
		int barrierHeight;
		int barrierEllipse;

		int spotBarrierLeft;
		int spotBarrierTop;
		int spotBlockLeft;
		int spotBlockTop;

	} render;

	struct Block
	{
		int blocksX = 10, blocksY = 18;
		int size = 35;
		int id = 1, nextId = 2;
		pair<int, int> pos[5];
		pair<int, int> data[20][5];
	} block;

	void SetBlockData(int blockId, int blockCnt, int posX, int posY);

	void UpdateBlockData(void);
	void UpdateDrawLength(void);
	void UpdateMap(void);

	void DrawWindow(void);
	void DrawBackgound(void);
	void DrawBarrier(void);
	void DrawMap(void);
	void DrawBlock(int posX, int posY);
	void DrawBlocks(void);
	void DrawGameEnd(void);

	void EventBlockMove(int moveX, int moveY);
	void EventBlockGenerate(void);
	void EventBlockChange(void);
	void EventKeyDown(void);
	void EventCleanFullLine(void);

	bool CheckBarrierTop(void);
	bool CheckBarrierButtom(void);
	bool CheckBarrierLeft(void);
	bool CheckBarrierRight(void);
	bool CheckGameEnd(void);

	bool CheckBlockValid(pair<int, int>* pos);
	bool CheckBlockDownBlock(void);
	bool CheckBlockLeftBlock(void);
	bool CheckBlockRightBlock(void);

};

int main()
{
	int blocksX = 10, blocksY = 18, blockSize = 35;
	Tetris game(blocksX, blocksY, blockSize);

	loadimage(&game.picBlocks[0], _T("assets/brown.png"), blockSize, blockSize);
	loadimage(&game.picBlocks[1], _T("assets/deep_blue.png"), blockSize, blockSize);
	loadimage(&game.picBlocks[2], _T("assets/green.png"), blockSize, blockSize);
	loadimage(&game.picBlocks[3], _T("assets/purple.png"), blockSize, blockSize);
	loadimage(&game.picBlocks[4], _T("assets/red.png"), blockSize, blockSize);
	loadimage(&game.picBlocks[5], _T("assets/shallow_blue.png"), blockSize, blockSize);
	loadimage(&game.picBlocks[6], _T("assets/yellow.png"), blockSize, blockSize);

	game.EventBlockGenerate();
	game.EventBlockGenerate();
	game.DrawWindow();

	while (true)
	{
		game.startTime = clock();

		BeginBatchDraw();
		cleardevice();

		game.EventCleanFullLine();
		game.EventKeyDown();

		game.DrawBackgound();
		game.DrawBarrier();

		if (game.CheckBarrierTop()) break;
		if (game.CheckBlockDownBlock() || game.CheckBarrierButtom())
		{
			game.UpdateMap();
			game.EventBlockGenerate();
		}

		if (game.cntFPS >= 15)
		{
			game.EventBlockMove(0, 1);
			game.cntFPS = 0;
		}

		game.DrawMap();
		game.DrawBlocks();

		EndBatchDraw();
		if (game.CheckGameEnd()) break;

		game.cntFPS++;
		game.endTime = clock();

		game.costTime = (game.endTime - game.startTime) % game.FPS;
		if (game.costTime < game.FPS)
		{
			Sleep(game.FPS - game.costTime);
		}
	}

	game.DrawGameEnd();
	Sleep(2000);
	return 0;
}

void Tetris::SetBlockData(int blockId, int blockCnt, int posX, int posY)
{
	block.data[blockId][blockCnt].X = posX;
	block.data[blockId][blockCnt].Y = posY;
}

void Tetris::UpdateBlockData(void)
{
	int centerPos = block.blocksX / 2;
	
	SetBlockData(1, 1, centerPos,		0);
	SetBlockData(1, 2, centerPos + 1,	0);
	SetBlockData(1, 3, centerPos,		-1);
	SetBlockData(1, 4, centerPos + 1,	-1);

	SetBlockData(2, 1, centerPos - 1,	0);
	SetBlockData(2, 2, centerPos,		0);
	SetBlockData(2, 3, centerPos + 1,	0);
	SetBlockData(2, 4, centerPos + 2,	0);

	SetBlockData(3, 1, centerPos,		0);
	SetBlockData(3, 2, centerPos,		-1);
	SetBlockData(3, 3, centerPos,		-2);
	SetBlockData(3, 4, centerPos,		-3);

	SetBlockData(4, 1, centerPos,		0);
	SetBlockData(4, 2, centerPos + 1,	0);
	SetBlockData(4, 3, centerPos + 1,	-1);
	SetBlockData(4, 4, centerPos + 2,	-1);

	SetBlockData(5, 1, centerPos + 1,	0);
	SetBlockData(5, 2, centerPos,		-1);
	SetBlockData(5, 3, centerPos + 1,	-1);
	SetBlockData(5, 4, centerPos,		-2);

	SetBlockData(6, 1, centerPos,		0);
	SetBlockData(6, 2, centerPos + 1,	0);
	SetBlockData(6, 3, centerPos - 1,	-1);
	SetBlockData(6, 4, centerPos,		-1);

	SetBlockData(7, 1, centerPos,		0);
	SetBlockData(7, 2, centerPos,		-1);
	SetBlockData(7, 3, centerPos + 1,	-1);
	SetBlockData(7, 4, centerPos + 1,	-2);

	SetBlockData(8, 1, centerPos - 1,	0);
	SetBlockData(8, 2, centerPos,		0);
	SetBlockData(8, 3, centerPos + 1,	0);
	SetBlockData(8, 4, centerPos,		-1);

	SetBlockData(9, 1, centerPos,		0);
	SetBlockData(9, 2, centerPos,		-1);
	SetBlockData(9, 3, centerPos + 1,	-1);
	SetBlockData(9, 4, centerPos,		-2);

	SetBlockData(10, 1, centerPos,		0);
	SetBlockData(10, 2, centerPos - 1,	-1);
	SetBlockData(10, 3, centerPos,		-1);
	SetBlockData(10, 4, centerPos + 1,	-1);

	SetBlockData(11, 1, centerPos,		0);
	SetBlockData(11, 2, centerPos - 1,	-1);
	SetBlockData(11, 3, centerPos,		-1);
	SetBlockData(11, 4, centerPos,		-2);

	SetBlockData(12, 1, centerPos,		0);
	SetBlockData(12, 2, centerPos + 1,	0);
	SetBlockData(12, 3, centerPos + 2,	0);
	SetBlockData(12, 4, centerPos,		-1);

	SetBlockData(13, 1, centerPos,		0);
	SetBlockData(13, 2, centerPos,		-1);
	SetBlockData(13, 3, centerPos,		-2);
	SetBlockData(13, 4, centerPos + 1,	-2);

	SetBlockData(14, 1, centerPos + 2,	0);
	SetBlockData(14, 2, centerPos,		-1);
	SetBlockData(14, 3, centerPos + 1,	-1);
	SetBlockData(14, 4, centerPos + 2,	-1);

	SetBlockData(15, 1, centerPos,		0);
	SetBlockData(15, 2, centerPos + 1,	0);
	SetBlockData(15, 3, centerPos + 1,	-1);
	SetBlockData(15, 4, centerPos + 1,	-2);

	SetBlockData(16, 1, centerPos,		0);
	SetBlockData(16, 2, centerPos + 1,	0);
	SetBlockData(16, 3, centerPos + 2,	0);
	SetBlockData(16, 4, centerPos + 2,	-1);

	SetBlockData(17, 1, centerPos,		0);
	SetBlockData(17, 2, centerPos + 1,	0);
	SetBlockData(17, 3, centerPos,		-1);
	SetBlockData(17, 4, centerPos,		-2);

	SetBlockData(18, 1, centerPos,		0);
	SetBlockData(18, 2, centerPos,		-1);
	SetBlockData(18, 3, centerPos + 1,	-1);
	SetBlockData(18, 4, centerPos + 2,	-1);

	SetBlockData(19, 1, centerPos + 1,	0);
	SetBlockData(19, 2, centerPos + 1,	-1);
	SetBlockData(19, 3, centerPos,		-2);
	SetBlockData(19, 4, centerPos + 1,	-2);
}

void Tetris::UpdateDrawLength(void)
{
	render.barrierWidth = render.barrierPadding * 2 + block.blocksX * block.size+ (block.blocksX - 1) * render.blockSpace;
	render.barrierHeight = render.barrierPadding * 2 + block.blocksY * block.size + (block.blocksY - 1) * render.blockSpace;
	
	render.windowWidth = render.windowPadding * 2 + render.barrierWidth + render.blockSpace + 0;
	render.windowHeight = render.windowPadding * 2 + render.barrierHeight;

	render.spotBarrierLeft = render.windowPadding;
	render.spotBarrierTop = render.spotBarrierLeft;
	render.spotBlockLeft = render.windowPadding + render.barrierPadding;
	render.spotBlockTop = render.spotBlockLeft;
}

void Tetris::UpdateMap(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		map[block.pos[cnt].X][block.pos[cnt].Y] = 1;
	}
}

void Tetris::DrawWindow()
{
	
	initgraph(render.windowWidth, render.windowHeight);
}

void Tetris::DrawBackgound(void)
{
	IMAGE bk;
	loadimage(&bk, _T("assets/gameBK.png"), 1239, 850);
	putimage(0, 0, &bk);
}

void Tetris::DrawBarrier(void)
{
	// draw bk
	setfillcolor(RGB(46, 48, 54));
	setlinecolor(BLACK);
	fillroundrect(render.spotBarrierLeft, render.spotBarrierTop,
		render.spotBarrierLeft + render.barrierWidth, render.spotBarrierTop + render.barrierHeight,
		render.barrierEllipse, render.barrierEllipse);
	// draw blocks
	setfillcolor(RGB(54, 57, 63));
	setlinecolor(RGB(54, 57, 63));
	for (int x = 1, y = 1; ; y++)
	{
		if (y > block.blocksY) y = 1, x++;
		if (x > block.blocksX) break;

		int right = render.spotBlockLeft + x * block.size + (x - 1) * render.blockSpace;
		int buttom = render.spotBlockTop + y * block.size + (y - 1) * render.blockSpace;
		fillroundrect(right - block.size, buttom - block.size, right, buttom,
			render.barrierEllipse / 2, render.barrierEllipse / 2);
	}
}

void Tetris::DrawMap(void)
{
	for (int x = 1, y= 1; ; y++)
	{
		if (y > block.blocksY) y = 1, x++;
		if (x > block.blocksX) break;
		if (map[x][y] == 1) DrawBlock(x, y);
	}
}

void Tetris::DrawBlock(int posX, int posY)
{
	int left = render.spotBlockLeft + (posX - 1) * (block.size + render.blockSpace);
	int top = render.spotBlockTop + (posY - 1) * (block.size + render.blockSpace);
	putimage(left, top, &picBlocks[colorId]);
}

void Tetris::DrawBlocks(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		if (block.pos[cnt].Y >= 1) DrawBlock(block.pos[cnt].X, block.pos[cnt].Y);
	}
}

void Tetris::DrawGameEnd(void)
{
	settextcolor(GREEN);
	setbkmode(TRANSPARENT);
	settextstyle(70, 0, _T("微软雅黑"));

	LOGFONT f;
	gettextstyle(&f);
	f.lfQuality = ANTIALIASED_QUALITY;
	f.lfWeight = FW_BLACK;
	//
	RECT r = { 0, 0, render.windowWidth, render.windowHeight };
	drawtext(_T("Game over!"), &r, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
}

void Tetris::EventBlockMove(int moveX, int moveY)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		block.pos[cnt].X += moveX;
		block.pos[cnt].Y += moveY;
	}
}

void Tetris::EventBlockGenerate(void)
{
	srand(int(time(0)));
	block.id = block.nextId;
	block.nextId = rand() % 19 + 1;
	colorId = rand() % 7;

	for (int cnt = 1; cnt <= 4; cnt++)
	{
		int x = block.data[block.id][cnt].X;
		int y = block.data[block.id][cnt].Y;
		block.pos[cnt] = { x, y };
	}
}

void Tetris::EventBlockChange(void)
{
	int newBlockId;
	int moveBlocksX;
	int moveBlocksY;
	pair<int, int> newPos[5];

	// calc down distance
	moveBlocksX = block.pos[1].X - block.data[block.id][1].X;
	moveBlocksY = block.pos[1].Y - block.data[block.id][1].Y;

	// next id
	switch (block.id)
	{
	case 2:
	case 4:  
	case 6:
	case 8:
	case 9:
	case 10:
	case 12: 
	case 13: 
	case 14:
	case 16: 
	case 17: 
	case 18:
		newBlockId = block.id + 1;
		break;
	case 3:
	case 5:
	case 7:
		newBlockId = block.id - 1;
		break;
	case 11:
	case 15:
	case 19:
		newBlockId = block.id - 3;
		break;
	default:
		newBlockId = block.id;
	}

	// calc newPos
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		newPos[cnt].X = block.data[newBlockId][cnt].X + moveBlocksX;
		newPos[cnt].Y = block.data[newBlockId][cnt].Y + moveBlocksY;
	}

	// check newPos valid
	if (CheckBlockValid(newPos))
	{// update pos

		block.id = newBlockId;
		for (int cnt = 1; cnt <= 4; cnt++)
		{
			block.pos[cnt].X = newPos[cnt].X;
			block.pos[cnt].Y = newPos[cnt].Y;
		}
	}
}

void Tetris::EventKeyDown(void)
{
	ExMessage key;
	do
	{
		if (!peekmessage(&key, EX_KEY)) break;
		if (key.message != WM_KEYDOWN) break;

		if (key.vkcode == VK_LEFT && !CheckBlockLeftBlock() && !CheckBarrierLeft())
			EventBlockMove(-1, 0);
		else if (key.vkcode == VK_RIGHT && !CheckBlockRightBlock() && !CheckBarrierRight())
			EventBlockMove(1, 0);
		else if (key.vkcode == VK_DOWN)
		{
			if (!CheckBlockDownBlock() || !CheckBarrierButtom())
				EventBlockMove(0, 1);
		}
		else if (key.vkcode == VK_UP)
			EventBlockChange();
		else cout << "Unkonwn key down" << endl;

		flushmessage(-1);

	} while (false);
}

void Tetris::EventCleanFullLine(void)
{
	for (int y = block.blocksY; y >= 1; y--)
	{
		bool isFull = true;
		for (int x = 1; x <= block.blocksX; x++)
		{
			if (map[x][y] != 1)
			{
				isFull = false;
				break;
			}
		}
		if (isFull)
		{
			for (int yy = y; yy >= 1; yy--)
			{
				for (int xx = 1; xx <= block.blocksX; xx++)
				{
					map[xx][yy] = map[xx][yy - 1];
				}
			}
			y++;
		}
	}
}

bool Tetris::CheckBarrierTop(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		if (block.pos[cnt].Y == 0 && 
			map[block.pos[cnt].X][1] == 1)
			return true;
	}
	return false;
}

bool Tetris::CheckBarrierButtom(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		if (block.pos[cnt].Y >= block.blocksY) return true;
	}
	return false;
}

bool Tetris::CheckBarrierLeft(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		if (block.pos[cnt].X <= 1) return true;
	}
	return false;
}

bool Tetris::CheckBarrierRight(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		if (block.pos[cnt].X >= block.blocksX) return true;
	}
	return false;
}

bool Tetris::CheckGameEnd(void)
{
	for (int x = 1; x <= block.blocksX; x++)
	{
		if (map[x][0] == 1) return true;
	}
	return false;
}

bool Tetris::CheckBlockValid(pair<int, int>* pos)
{
	// check block hit block
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		int x = pos[cnt].X;
		int y = pos[cnt].Y;
		if (x < 1 || x > block.blocksX) return false;
		if (y < 1 || y > block.blocksY) return false;
		if (map[x][y] == 1) return false;
	}
	return true;
}

bool Tetris::CheckBlockDownBlock(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		if (map[block.pos[cnt].X][block.pos[cnt].Y + 1] == 1) return true;
	}
	return false;
}

bool Tetris::CheckBlockLeftBlock(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		int x = block.pos[cnt].X - 1;
		int y = block.pos[cnt].Y;
		if (map[x][y] == 1) return true;
	}
	return false;
}

bool Tetris::CheckBlockRightBlock(void)
{
	for (int cnt = 1; cnt <= 4; cnt++)
	{
		int x = block.pos[cnt].X + 1;
		int y = block.pos[cnt].Y;
		if (map[x][y] == 1) return true;
	}
	return false;
}

```

