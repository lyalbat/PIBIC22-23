# specifying the path
path <- "/home/larissa/Research/LACCAN/Meu/Multivariate_air_pollution/repositorio/PIBIC22-23/datasets/airpol.csv"
content <- read.csv(path,header=TRUE)
typeof(content)

install.packages("sp")
library(sp)
install.packages("gstat")
library(gstat)
data(meuse)
class(meuse)
print(meuse)
