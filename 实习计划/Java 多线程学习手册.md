# Java 多线程学习手册：从入门到实习实战

## 第一章 Java 多线程基础
### 1.1 进程与线程的概念
- **进程**：操作系统分配资源的最小单位，每个进程有独立的内存空间。
- **线程**：CPU 调度的最小单位，是进程中的执行流，多个线程共享进程的堆和方法区，但有独立的程序计数器、虚拟机栈和本地方法栈。
- **关系**：一个进程可以包含多个线程，线程是进程的“轻量级”执行单元。

### 1.2 Java 中创建线程的三种方式
#### 方式一：继承 `Thread` 类
```java
// 自定义线程类继承 Thread
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("线程执行：" + Thread.currentThread().getName());
    }
}

// 使用
public class ThreadDemo {
    public static void main(String[] args) {
        MyThread t1 = new MyThread();
        t1.start(); // 启动线程（注意：不能直接调用 run()）
    }
}
```

#### 方式二：实现 `Runnable` 接口（推荐）
```java
// 实现 Runnable 接口
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("线程执行：" + Thread.currentThread().getName());
    }
}

// 使用
public class RunnableDemo {
    public static void main(String[] args) {
        MyRunnable runnable = new MyRunnable();
        Thread t2 = new Thread(runnable);
        t2.start();
        
        // Lambda 表达式简化（Java 8+）
        new Thread(() -> System.out.println("Lambda 线程")).start();
    }
}
```

#### 方式三：使用 `Callable` 和 `Future`（带返回值）
```java
import java.util.concurrent.Callable;
import java.util.concurrent.FutureTask;

// 实现 Callable 接口
class MyCallable implements Callable<Integer> {
    @Override
    public Integer call() throws Exception {
        System.out.println("线程执行：" + Thread.currentThread().getName());
        return 42; // 带返回值
    }
}

// 使用
public class CallableDemo {
    public static void main(String[] args) throws Exception {
        MyCallable callable = new MyCallable();
        FutureTask<Integer> futureTask = new FutureTask<>(callable);
        new Thread(futureTask).start();
        
        Integer result = futureTask.get(); // 阻塞等待线程执行完成并获取结果
        System.out.println("线程返回结果：" + result);
    }
}
```

### 1.3 线程的生命周期
Java 线程有 5 种状态，通过 `Thread.getState()` 可获取：
1. **NEW（新建）**：线程对象刚创建，未调用 `start()`。
2. **RUNNABLE（就绪/运行）**：线程已调用 `start()`，等待 CPU 调度或正在执行。
3. **BLOCKED（阻塞）**：线程等待锁资源（如进入 `synchronized` 块失败）。
4. **WAITING（无限等待）**：线程调用 `wait()`、`join()` 等方法，需其他线程唤醒。
5. **TIMED_WAITING（计时等待）**：线程调用 `sleep(long)`、`wait(long)` 等方法，超时后自动恢复。
6. **TERMINATED（终止）**：线程执行完成或异常退出。

### 1.4 练习题
1. 用 `Thread` 和 `Runnable` 分别创建 3 个线程，每个线程打印 1-5 的数字。
2. 用 `Callable` 创建线程，计算 1-100 的和并返回结果。
3. 观察线程状态：创建一个线程，分别在 `start()` 前、`start()` 后、`sleep()` 时、执行完后打印其状态。

---

## 第二章 线程的基本控制
### 2.1 `start()` 与 `run()` 的区别
- `start()`：启动线程，让线程进入 **RUNNABLE** 状态，由 JVM 调用 `run()` 方法（多线程执行）。
- `run()`：只是普通方法调用，不会启动新线程（单线程执行）。

### 2.2 线程休眠：`sleep(long millis)`
- 作用：让当前线程暂停指定毫秒数，进入 **TIMED_WAITING** 状态，不释放锁。
- 示例：
```java
public class SleepDemo {
    public static void main(String[] args) throws InterruptedException {
        for (int i = 0; i < 5; i++) {
            System.out.println(i);
            Thread.sleep(1000); // 休眠 1 秒
        }
    }
}
```

### 2.3 线程等待与通知：`wait()`、`notify()`、`notifyAll()`
- 这些方法必须在 **synchronized** 块/方法中调用（需持有锁）。
- `wait()`：让当前线程释放锁并进入 **WAITING** 状态，等待其他线程唤醒。
- `notify()`：随机唤醒一个正在等待的线程。
- `notifyAll()`：唤醒所有正在等待的线程。

**示例：生产者-消费者模型（简单版）**
```java
class SharedResource {
    private int data;
    private boolean hasData = false;

    // 生产者方法
    public synchronized void produce(int value) throws InterruptedException {
        while (hasData) { // 用 while 防止虚假唤醒
            wait(); // 等待消费者消费
        }
        data = value;
        hasData = true;
        System.out.println("生产：" + data);
        notify(); // 唤醒消费者
    }

    // 消费者方法
    public synchronized void consume() throws InterruptedException {
        while (!hasData) {
            wait(); // 等待生产者生产
        }
        System.out.println("消费：" + data);
        hasData = false;
        notify(); // 唤醒生产者
    }
}

// 使用
public class WaitNotifyDemo {
    public static void main(String[] args) {
        SharedResource resource = new SharedResource();
        new Thread(() -> {
            try {
                for (int i = 1; i <= 5; i++) resource.produce(i);
            } catch (InterruptedException e) { e.printStackTrace(); }
        }, "生产者").start();

        new Thread(() -> {
            try {
                for (int i = 1; i <= 5; i++) resource.consume();
            } catch (InterruptedException e) { e.printStackTrace(); }
        }, "消费者").start();
    }
}
```

### 2.4 线程加入：`join()`
- 作用：让当前线程等待调用 `join()` 的线程执行完毕后再继续执行。
- 示例：
```java
public class JoinDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread t = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                System.out.println("子线程执行：" + i);
                try { Thread.sleep(500); } catch (InterruptedException e) {}
            }
        });
        t.start();
        t.join(); // 主线程等待子线程执行完
        System.out.println("主线程执行完毕");
    }
}
```

### 2.5 线程中断：`interrupt()`
- 作用：给线程发送中断信号，但不会直接停止线程，需线程自身响应中断。
- 相关方法：
  - `interrupt()`：设置中断标志位为 `true`。
  - `isInterrupted()`：检查中断标志位。
  - `interrupted()`：检查并清除中断标志位（静态方法）。
- 示例：
```java
public class InterruptDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread t = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                System.out.println("线程运行中...");
                try {
                    Thread.sleep(500); // sleep 会响应中断并抛出异常，清除标志位
                } catch (InterruptedException e) {
                    System.out.println("线程被中断，准备退出");
                    Thread.currentThread().interrupt(); // 重新设置标志位，让循环退出
                }
            }
        });
        t.start();
        Thread.sleep(2000);
        t.interrupt(); // 发送中断信号
    }
}
```

### 2.6 线程让步：`yield()`
- 作用：让当前线程放弃 CPU 时间片，回到 **RUNNABLE** 状态，让其他线程执行（仅作提示，不保证一定生效）。

### 2.7 练习题
1. 用 `wait()` 和 `notify()` 实现两个线程交替打印 1-100（线程 1 打印奇数，线程 2 打印偶数）。
2. 主线程创建 3 个子线程，分别打印 A、B、C，要求主线程等待所有子线程执行完后再打印 "Done"（用 `join()`）。
3. 设计一个线程，在循环中打印数字，当主线程调用 `interrupt()` 后，线程安全退出。

---

## 第三章 线程安全与同步机制
### 3.1 线程安全问题的产生
当多个线程同时访问**共享可变资源**时，可能出现数据不一致。

**示例：非线程安全的计数器**
```java
class Counter {
    private int count = 0;
    public void increment() { count++; } // 非原子操作
    public int getCount() { return count; }
}

public class UnsafeDemo {
    public static void main(String[] args) throws InterruptedException {
        Counter counter = new Counter();
        Thread t1 = new Thread(() -> { for (int i = 0; i < 10000; i++) counter.increment(); });
        Thread t2 = new Thread(() -> { for (int i = 0; i < 10000; i++) counter.increment(); });
        t1.start(); t2.start();
        t1.join(); t2.join();
        System.out.println("最终计数：" + counter.getCount()); // 结果可能小于 20000
    }
}
```

### 3.2 `synchronized` 关键字
- 作用：保证同一时间只有一个线程执行指定代码块/方法，保证原子性、可见性、有序性。
- 使用方式：
  1. **同步实例方法**：锁对象是 `this`。
  2. **同步静态方法**：锁对象是类的 `Class` 对象。
  3. **同步代码块**：锁对象是自定义对象（推荐，粒度更细）。

**示例：用 synchronized 修复计数器**
```java
class SafeCounter {
    private int count = 0;
    // 同步方法
    public synchronized void increment() { count++; }
    // 或同步代码块
    public void increment2() {
        synchronized (this) { count++; }
    }
    public int getCount() { return count; }
}
```

### 3.3 `volatile` 关键字
- 作用：保证变量的**可见性**（一个线程修改变量，其他线程立即可见）和**禁止指令重排序**，但不保证原子性。
- 适用场景：状态标记（如 `boolean flag = true;`）。

**示例：volatile 状态标记**
```java
class VolatileDemo {
    private volatile boolean flag = true;
    public void run() {
        while (flag) { /* 执行任务 */ }
        System.out.println("线程停止");
    }
    public void stop() { flag = false; }
}
```

### 3.4 原子类（`java.util.concurrent.atomic`）
- 提供原子操作的类，如 `AtomicInteger`、`AtomicLong`、`AtomicBoolean` 等，底层基于 CAS（Compare-And-Swap）实现。

**示例：AtomicInteger 计数器**
```java
import java.util.concurrent.atomic.AtomicInteger;

class AtomicCounter {
    private AtomicInteger count = new AtomicInteger(0);
    public void increment() { count.incrementAndGet(); } // 原子递增
    public int getCount() { return count.get(); }
}
```

### 3.5 `Lock` 接口与 `ReentrantLock`
- `Lock` 是更灵活的锁机制，需手动加锁和解锁，支持公平锁、非公平锁、可中断锁等。
- 常用实现：`ReentrantLock`（可重入锁）。

**示例：ReentrantLock 修复计数器**
```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

class LockCounter {
    private int count = 0;
    private Lock lock = new ReentrantLock(); // 默认非公平锁
    public void increment() {
        lock.lock(); // 加锁
        try {
            count++;
        } finally {
            lock.unlock(); // 必须在 finally 中解锁，防止死锁
        }
    }
    public int getCount() { return count; }
}
```

### 3.6 死锁
- 定义：两个或多个线程互相等待对方释放锁，导致永久阻塞。
- 产生条件：
  1. 互斥条件：锁只能被一个线程持有。
  2. 请求与保持条件：线程持有锁的同时请求新锁。
  3. 不剥夺条件：锁不能被强制剥夺，只能主动释放。
  4. 循环等待条件：线程形成循环等待链。
- 避免方法：破坏上述任一条件（如按固定顺序获取锁）。

**示例：死锁演示**
```java
class DeadLockDemo {
    private static Object lock1 = new Object();
    private static Object lock2 = new Object();

    public static void main(String[] args) {
        new Thread(() -> {
            synchronized (lock1) {
                System.out.println("线程1持有lock1，等待lock2");
                try { Thread.sleep(100); } catch (InterruptedException e) {}
                synchronized (lock2) { System.out.println("线程1持有lock1和lock2"); }
            }
        }).start();

        new Thread(() -> {
            synchronized (lock2) {
                System.out.println("线程2持有lock2，等待lock1");
                try { Thread.sleep(100); } catch (InterruptedException e) {}
                synchronized (lock1) { System.out.println("线程2持有lock2和lock1"); }
            }
        }).start();
    }
}
```

### 3.7 练习题
1. 用 `synchronized` 实现线程安全的单例模式（双重检查锁定）。
2. 用 `ReentrantLock` 实现生产者-消费者模型。
3. 设计一个程序，演示死锁，并修改代码避免死锁（如按固定顺序获取锁）。
4. 用 `AtomicInteger` 实现一个线程安全的计数器，并测试 10 个线程各递增 10000 次的结果。

---

## 第四章 线程池
### 4.1 线程池的概念与优势
- 线程池：预先创建若干线程，放入池中，需要时直接取用，用完放回，避免频繁创建和销毁线程的开销。
- 优势：降低资源消耗、提高响应速度、便于线程管理。

### 4.2 `ThreadPoolExecutor` 核心参数
Java 线程池的核心实现是 `ThreadPoolExecutor`，构造参数如下：
```java
public ThreadPoolExecutor(
    int corePoolSize,         // 核心线程数（即使空闲也保留）
    int maximumPoolSize,      // 最大线程数
    long keepAliveTime,       // 非核心线程空闲存活时间
    TimeUnit unit,            // 时间单位
    BlockingQueue<Runnable> workQueue, // 任务队列
    ThreadFactory threadFactory,       // 线程工厂（创建线程）
    RejectedExecutionHandler handler    // 拒绝策略（任务满时的处理）
)
```

**任务执行流程**：
1. 线程数 < 核心线程数 → 创建核心线程执行任务。
2. 线程数 ≥ 核心线程数 → 任务加入队列。
3. 队列满 → 创建非核心线程执行任务。
4. 线程数 = 最大线程数且队列满 → 执行拒绝策略。

**常见拒绝策略**：
- `AbortPolicy`：默认，抛出异常。
- `CallerRunsPolicy`：由调用线程执行任务。
- `DiscardPolicy`：直接丢弃任务。
- `DiscardOldestPolicy`：丢弃队列中最老的任务，执行当前任务。

### 4.3 常见的线程池类型（`Executors` 工具类）
#### 1. `FixedThreadPool`（固定大小线程池）
```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

// 核心线程数 = 最大线程数，队列无界
ExecutorService fixedPool = Executors.newFixedThreadPool(3);
```

#### 2. `CachedThreadPool`（可缓存线程池）
```java
// 核心线程数=0，最大线程数=Integer.MAX_VALUE，线程空闲 60 秒回收
ExecutorService cachedPool = Executors.newCachedThreadPool();
```

#### 3. `SingleThreadExecutor`（单线程线程池）
```java
// 核心线程数=最大线程数=1，保证任务按顺序执行
ExecutorService singlePool = Executors.newSingleThreadExecutor();
```

#### 4. `ScheduledThreadPool`（定时任务线程池）
```java
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

// 支持定时和周期性任务
ScheduledExecutorService scheduledPool = Executors.newScheduledThreadPool(2);
// 延迟 1 秒执行
scheduledPool.schedule(() -> System.out.println("延迟任务"), 1, TimeUnit.SECONDS);
// 延迟 1 秒后，每 2 秒执行一次
scheduledPool.scheduleAtFixedRate(() -> System.out.println("周期任务"), 1, 2, TimeUnit.SECONDS);
```

### 4.4 线程池的合理配置
- **CPU 密集型任务**：核心线程数 = CPU 核心数 + 1（如 `Runtime.getRuntime().availableProcessors() + 1`）。
- **I/O 密集型任务**：核心线程数 = 2 * CPU 核心数（或根据实际压测调整）。

**示例：自定义线程池（推荐，避免 OOM）**
```java
import java.util.concurrent.*;

public class ThreadPoolDemo {
    public static void main(String[] args) {
        // 自定义线程池
        ThreadPoolExecutor pool = new ThreadPoolExecutor(
            2,                          // 核心线程数
            5,                          // 最大线程数
            60L, TimeUnit.SECONDS,      // 空闲时间
            new LinkedBlockingQueue<>(10), // 有界队列（容量 10）
            Executors.defaultThreadFactory(),
            new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
        );

        // 提交任务
        for (int i = 0; i < 20; i++) {
            final int taskId = i;
            pool.execute(() -> {
                System.out.println("线程 " + Thread.currentThread().getName() + " 执行任务 " + taskId);
                try { Thread.sleep(1000); } catch (InterruptedException e) {}
            });
        }

        pool.shutdown(); // 关闭线程池（等待任务执行完）
    }
}
```

### 4.5 练习题
1. 用 `FixedThreadPool` 提交 10 个任务，每个任务打印当前线程名和任务编号。
2. 自定义一个线程池，核心线程数 3，最大线程数 6，队列容量 5，拒绝策略为 `CallerRunsPolicy`，提交 20 个任务观察执行情况。
3. 用 `ScheduledThreadPool` 实现一个定时任务，每隔 3 秒打印一次当前时间。
4. 设计一个程序，对比 `FixedThreadPool` 和 `CachedThreadPool` 执行 100 个短任务的效率。

---

## 第五章 并发工具类
### 5.1 `CountDownLatch`（倒计时门闩）
- 作用：让一个或多个线程等待其他线程完成后再执行。
- 核心方法：
  - `CountDownLatch(int count)`：构造函数，count 为等待的线程数。
  - `countDown()`：count 减 1。
  - `await()`：等待 count 变为 0。

**示例：主线程等待 3 个子线程执行完**
```java
import java.util.concurrent.CountDownLatch;

public class CountDownLatchDemo {
    public static void main(String[] args) throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(3);
        for (int i = 0; i < 3; i++) {
            final int id = i;
            new Thread(() -> {
                System.out.println("线程 " + id + " 执行完毕");
                latch.countDown(); // 计数减 1
            }).start();
        }
        latch.await(); // 主线程等待
        System.out.println("所有线程执行完毕，主线程继续");
    }
}
```

### 5.2 `CyclicBarrier`（循环屏障）
- 作用：让多个线程互相等待，到达屏障点后一起执行。
- 核心方法：
  - `CyclicBarrier(int parties)`：parties 为等待的线程数。
  - `await()`：线程到达屏障点，等待其他线程。

**示例：3 个线程到达屏障点后一起执行**
```java
import java.util.concurrent.CyclicBarrier;

public class CyclicBarrierDemo {
    public static void main(String[] args) {
        CyclicBarrier barrier = new CyclicBarrier(3, () -> System.out.println("所有线程到达屏障点，开始执行后续任务"));
        for (int i = 0; i < 3; i++) {
            final int id = i;
            new Thread(() -> {
                System.out.println("线程 " + id + " 到达屏障点");
                try {
                    barrier.await(); // 等待其他线程
                    System.out.println("线程 " + id + " 继续执行");
                } catch (Exception e) { e.printStackTrace(); }
            }).start();
        }
    }
}
```

### 5.3 `Semaphore`（信号量）
- 作用：控制同时访问资源的线程数量（限流）。
- 核心方法：
  - `Semaphore(int permits)`：permits 为许可数。
  - `acquire()`：获取许可（无许可则阻塞）。
  - `release()`：释放许可。

**示例：限制最多 3 个线程同时执行**
```java
import java.util.concurrent.Semaphore;

public class SemaphoreDemo {
    public static void main(String[] args) {
        Semaphore semaphore = new Semaphore(3);
        for (int i = 0; i < 10; i++) {
            final int id = i;
            new Thread(() -> {
                try {
                    semaphore.acquire(); // 获取许可
                    System.out.println("线程 " + id + " 获得许可，开始执行");
                    Thread.sleep(1000);
                    System.out.println("线程 " + id + " 执行完毕，释放许可");
                    semaphore.release(); // 释放许可
                } catch (InterruptedException e) { e.printStackTrace(); }
            }).start();
        }
    }
}
```

### 5.4 `Exchanger`（交换器）
- 作用：两个线程在同步点交换数据。
- 核心方法：`exchange(V x)`：交换数据，阻塞等待另一个线程。

**示例：两个线程交换字符串**
```java
import java.util.concurrent.Exchanger;

public class ExchangerDemo {
    public static void main(String[] args) {
        Exchanger<String> exchanger = new Exchanger<>();
        new Thread(() -> {
            try {
                String data1 = "线程1的数据";
                System.out.println("线程1准备交换：" + data1);
                String received = exchanger.exchange(data1);
                System.out.println("线程1收到：" + received);
            } catch (InterruptedException e) { e.printStackTrace(); }
        }).start();

        new Thread(() -> {
            try {
                String data2 = "线程2的数据";
                System.out.println("线程2准备交换：" + data2);
                Thread.sleep(1000); // 模拟延迟
                String received = exchanger.exchange(data2);
                System.out.println("线程2收到：" + received);
            } catch (InterruptedException e) { e.printStackTrace(); }
        }).start();
    }
}
```

### 5.5 练习题
1. 用 `CountDownLatch` 模拟 100 米赛跑：5 个运动员线程，主线程等待所有运动员到达终点后宣布比赛结束。
2. 用 `CyclicBarrier` 模拟 3 个玩家加载游戏，全部加载完成后一起进入游戏。
3. 用 `Semaphore` 实现一个数据库连接池，限制最多 5 个连接。
4. 用 `Exchanger` 实现两个线程交换整数数组。

---

## 第六章 高级并发主题
### 6.1 `ThreadLocal`
- 作用：为每个线程提供独立的变量副本，线程间互不影响。
- 核心方法：
  - `set(T value)`：设置当前线程的变量值。
  - `get()`：获取当前线程的变量值。
  - `remove()`：移除当前线程的变量值（防止内存泄漏）。

**示例：ThreadLocal 存储用户信息**
```java
class UserContext {
    private static ThreadLocal<String> userHolder = new ThreadLocal<>();
    public static void setUser(String user) { userHolder.set(user); }
    public static String getUser() { return userHolder.get(); }
    public static void clear() { userHolder.remove(); } // 必须清理
}

public class ThreadLocalDemo {
    public static void main(String[] args) {
        new Thread(() -> {
            UserContext.setUser("用户A");
            System.out.println("线程1：" + UserContext.getUser());
            UserContext.clear();
        }).start();

        new Thread(() -> {
            UserContext.setUser("用户B");
            System.out.println("线程2：" + UserContext.getUser());
            UserContext.clear();
        }).start();
    }
}
```

### 6.2 并发集合
- `ConcurrentHashMap`：线程安全的 HashMap（替代 `Hashtable`）。
- `CopyOnWriteArrayList`：线程安全的 ArrayList（读多写少场景）。
- `CopyOnWriteArraySet`：线程安全的 Set。
- `ConcurrentLinkedQueue`：线程安全的无界队列。

**示例：ConcurrentHashMap 使用**
```java
import java.util.concurrent.ConcurrentHashMap;

public class ConcurrentHashMapDemo {
    public static void main(String[] args) {
        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
        map.put("A", 1);
        map.put("B", 2);
        System.out.println(map.get("A"));
    }
}
```

### 6.3 `Future` 与 `FutureTask`
- `Future`：表示异步计算的结果，可检查计算是否完成、获取结果。
- `FutureTask`：`Future` 的实现类，可包装 `Callable` 或 `Runnable`。

**示例：Future 获取异步任务结果**
```java
import java.util.concurrent.*;

public class FutureDemo {
    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(1);
        Future<Integer> future = pool.submit(() -> {
            Thread.sleep(1000);
            return 42;
        });
        System.out.println("等待结果...");
        Integer result = future.get(); // 阻塞等待
        System.out.println("结果：" + result);
        pool.shutdown();
    }
}
```

### 6.4 `CompletableFuture` 异步编程
- Java 8 引入，支持链式调用、组合多个异步任务、异常处理等。

**示例：CompletableFuture 链式调用**
```java
import java.util.concurrent.CompletableFuture;

public class CompletableFutureDemo {
    public static void main(String[] args) {
        // 异步任务1：计算 1+2
        CompletableFuture<Integer> future1 = CompletableFuture.supplyAsync(() -> {
            System.out.println("任务1执行");
            return 1 + 2;
        });

        // 任务2：接收任务1结果，乘以 3
        CompletableFuture<Integer> future2 = future1.thenApplyAsync(result -> {
            System.out.println("任务2执行，输入：" + result);
            return result * 3;
        });

        // 任务3：接收任务2结果，打印
        future2.thenAccept(result -> System.out.println("最终结果：" + result));

        // 等待所有任务完成
        CompletableFuture.allOf(future1, future2).join();
    }
}
```

### 6.5 练习题
1. 用 `ThreadLocal` 实现一个简单的事务上下文，存储当前线程的事务 ID。
2. 用 `ConcurrentHashMap` 统计 10 个线程并发写入 10000 个键值对后的大小。
3. 用 `CompletableFuture` 实现：异步查询用户信息，再异步查询用户订单，最后合并结果打印。
4. 设计一个程序，对比 `HashMap` 和 `ConcurrentHashMap` 在多线程并发写入时的安全性。

---

## 实习实战建议
1. **重点掌握**：线程池配置、`synchronized`/`Lock` 线程安全、`CompletableFuture` 异步编程、并发集合。
2. **实践项目**：
   - 实现一个简单的异步任务处理系统（用线程池 + `CompletableFuture`）。
   - 设计一个高并发的秒杀系统（用 `Semaphore` 限流、`ConcurrentHashMap` 存储库存）。
3. **面试准备**：
   - 线程池参数、执行流程、拒绝策略。
   - `synchronized` 和 `Lock` 的区别。
   - `volatile` 的作用和原理。
   - `ConcurrentHashMap` 的底层实现（JDK 1.8 版本）。

需要我帮你**详细解析某个章节的练习题答案**，或者**针对某个实战场景提供代码示例**吗？











# 答疑解惑



我帮你把这段学习过程中的关键问题，整理成一套**结构清晰、可复习、可用于面试表达的问题清单**👇

------

## 🧠 一、核心问题（你最初的困惑）

1. **为什么使用 `wait()` / `notify()` 的代码不能实现线程交替执行？**
2. **线程之间如果没有共享变量，是否还能进行通信？**
3. **仅靠参数（如 `n`）判断条件，为什么会导致线程无法协作甚至死锁？**

------

## 🔄 二、机制理解类问题（wait / notify 本质）

1. **`wait()` 和 `notify()` 在 Java 中的本质是什么？**
2. **调用 `wait()` 时，线程具体发生了什么？（锁、状态、执行位置）**
3. **调用 `notify()` 后，被唤醒的线程会立即执行吗？**
4. **`notify()` 和 `notifyAll()` 的区别是什么？什么时候必须用 `notifyAll()`？**
5. **为什么 `wait()` / `notify()` 必须写在 `synchronized` 代码块中？**

------

## 🔁 三、执行流程类问题（非常关键）

1. **线程从 `wait()` 被唤醒后，是从头执行，还是从 `wait()` 之后继续执行？**
2. **被 `notify()` 唤醒的线程，为什么还需要重新竞争锁？**
3. **一个完整的 wait → notify → 执行 的线程调度流程是怎样的？**

------

## ⚠️ 四、常见错误与陷阱（你已经踩到的坑）

1. **为什么必须用 `while` 而不是 `if` 来包裹 `wait()`？**
2. **什么是“虚假唤醒”（spurious wakeup）？**
3. **为什么没有共享状态变量会导致线程无法正确协作？**
4. **为什么 `notify()` 可能导致线程“卡死”或“饿死”？**

------

## 🧩 五、设计思想类问题（本质提升）

1. **线程交替执行的本质是什么？（不是奇偶判断，而是执行顺序控制）**
2. **线程通信的三要素是什么？**

- 共享变量
- 条件判断
- 同步机制

------

## 🚀 六、扩展与进阶问题（更现代的写法）

1. **`wait/notify` 是否是唯一的线程通信方式？**
2. **`ReentrantLock + Condition` 和 `wait/notify` 的区别是什么？**
3. **什么时候应该使用 `BlockingQueue` 替代手写线程同步？**
4. **`Semaphore`、`CountDownLatch`、`CyclicBarrier` 分别适用于什么场景？**

------

## 🎯 最终总结（一句话版本）

你这一整串问题，本质可以归纳为一句话：

> 👉 **Java 线程如何基于共享状态，实现“可控的执行顺序”？**

而你已经在逐步掌握：

- ✔ 线程通信（wait/notify）
- ✔ 执行调度机制
- ✔ 并发设计思想

------

## 📌 如果你想再进一层（强烈建议）

可以把这些问题升级成面试级表达：

👉 “请你设计一个多线程交替执行的方案，并分析不同实现方式的优劣”

我可以帮你把这一整套整理成**面试标准答案 + 模板代码 + 思路图**，让你这一块直接超过大多数人 👍





---







我帮你把刚才的问题整理成更清晰、结构化的版本（适合笔记/面试表达）：

------

## 🎯 问题整理：Java 多线程中 `join()` 的行为

在 Java 多线程编程中，当主线程通过 `join()` 等待多个子线程时，我有以下几个疑问：

### 1️⃣ 子线程执行顺序问题

- 当存在多个子线程时：
  - 子线程的执行顺序是否会按照 `join()` 的调用顺序来执行？
  - 还是说子线程的执行顺序是完全不确定的？

------

### 2️⃣ 主线程阻塞机制

- 当主线程依次调用多个 `join()`：

  ```java
  t1.join();
  t2.join();
  t3.join();
  ```

  - 主线程是否会：
    - 先阻塞在 `t1.join()`？
    - 等 t1 执行完后，再执行 `t2.join()`？
  - 是否可以理解为：**主线程是“按 join 顺序逐个等待线程”？**

------

### 3️⃣ join 顺序与执行结果的关系

- 如果：

  ```java
  t1.start();
  t2.start();
  
  t2.join();
  t1.join();
  ```

  - 是否意味着：
    - t2 一定比 t1 先执行完？
  - 还是说：
    - `join()` 只影响主线程等待顺序，不影响子线程执行顺序？

------

### 4️⃣ 线程执行控制能力

- `join()` 是否可以用于控制线程执行顺序？

- 如果想让线程严格按顺序执行（如 t1 → t2 → t3），是否必须：

  ```java
  t1.start();
  t1.join();
  
  t2.start();
  t2.join();
  
  t3.start();
  t3.join();
  ```

------

## 🧠 核心疑问总结（一句话版）

> 在 Java 多线程中，`join()` 到底是：
>
> - 控制“线程执行顺序”
> - 还是仅仅控制“主线程等待顺序”？



