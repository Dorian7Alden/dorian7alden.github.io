【黑马mybatis教程全套视频教程，2天Mybatis框架从入门到精通】https://www.bilibili.com/video/BV1MT4y1k7wZ?p=10&vd_source=b6e1ca78539fba73d35a26224eac9099





- where 都用 \<where\> 关键字
- 使用恒等式 1=1



类似于 switch case 的作用。只有一个起作用

\<choose\>

​	\<when test="" \>



​	\<when\>

​	\<otherwise\>



​	\<otherwise\>

\<choose\>





- 查询回显：添加主键返回，设置两个属性：是否生成+绑定主键



\<set\> 标签跟 \<where\> 一样的作用，就是在使用 UPDATE 的时候嵌套即可



\<foreach\> 用来遍历，常用来批量删除功能

- 默认传参会被封装成 map 类型，默认 key 为 array，value 就是对应的数组，collection="array"
- 通过 @Param 来指定 key 值
- seperator 指定分隔符
- open 开始拼接
- close 结束拼接



