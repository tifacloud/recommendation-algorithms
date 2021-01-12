# Recommendation Algorithms
Some recommendation algorithms for data related experiment and scientific research  
一些推荐算法供与数据相关的实验和科学研究使用

## 运行环境
- python 2.7及之前版本
- python库：MySQLdb, matplotlib, PIL

## 使用帮助
1.安装MySQL，在main.py文件中的gen_rand_usr函数中配置数据库相关参数，使用movie_data.sql文件导入测试数据，测试数据使用的是movielens 100k数据集  
2.执行main.py文件即可得到各个推荐算法的运行结果

## 结果说明
结果包含了四个算法运行后的推荐的精确率和召回率。四个算法分别为：1.以传统的协同过滤算法为基础的推荐算法；2.以协同过滤为基础，使用k均值聚类和退火算法进行优化的推荐算法；3.以协同过滤为基础，使用k均值聚类和遗传算法进行优化的推荐算法；4.以协同过滤为基础，使用k均值聚类和博弈论均衡模型进行优化的推荐算法。
