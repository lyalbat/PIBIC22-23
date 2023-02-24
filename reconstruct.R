library(gstat)
#library(geobr)
library(hash)
library(sp)
library(tidyr)
library(EnvStats)
library(png)

#-------------------------------------------------------------------------------------

grouping_series <- function() {

	my_files <- list.files('/home/larissa/Documents/airPolution/dataframes_snapshots/')
	
	snapshots_group <- list()
	for (i in seq_along(my_files)) {
	    path = paste("/home/larissa/Documents/airPolution/dataframes_snapshots/", my_files[i],sep="")
	    snapshots_group[[i]] <- read.csv(file = path)
	}
	
	return(snapshots_group)
}

#-------------------------------------------------------------------------------------

var_name_choice <- function(csvFile){
	headers <- names(csvFile)
	if(tail(headers, n=1) == "O3"){
		pollutants <- c("CO", "PM10", "O3")}
	else if(tail(headers, n=1) == "NO2"){
		pollutants <- "NO2"}
	else if(tail(headers, n=1) == "SO2"){
		pollutants <- "SO2"
	}
	#Checking for errors in the reading
	else{
		return ("Error")}
	return (pollutants)
}
#-------------------------------------------------------------------------------------

# Build a temporal sequence with 
predict_series <- function(snapshot_series, var_names, coords) {

	timeserie_map <- list()
	matern <- NULL


	for(i in 1:length(snapshot_series)) {
		airpol_snapshot <- snapshot_series[[i]]
		airpol.g <- NULL

		if(is.element("CO", var_names))
			airpol.g <- gstat(id="CO", 
					  formula= log(unlist(airpol_snapshot$CO)) ~ 1,
					  data=airpol_snapshot, 
					  nmax = 10)

		if(is.element("PM10", var_names))
			airpol.g <- gstat(airpol.g, 
					  "PM10", 
					  log(unlist(airpol_snapshot$PM10))~1,
					  data=airpol_snapshot, 
					  nmax = 10)

		if(is.element("O3", var_names))
			airpol.g <- gstat(airpol.g, 
					  "O3", 
					  log(unlist(airpol_snapshot$O3))~1,
					  airpol_snapshot, 
					  nmax = 10)

		if(is.element("NO2", var_names))
			airpol.g <- gstat(airpol.g, 
					  "NO2", 
					  log(unlist(airpol_snapshot$NO2))~1,
					  airpol_snapshot, 
					  nmax = 10)

		if(is.element("SO2", var_names))
			airpol.g <- gstat(airpol.g, 
					  "SO2", 
					  log(unlist(airpol_snapshot$SO2))~1,
					  airpol_snapshot, 
					  nmax = 10)


		#matern=vgm(0.1, "Mat", 3, kappa=0.5)

		#if(is.element("NO2", var_names))
			matern=vgm(5, "Mat", 3, kappa=0.5)

		airpol.g <- gstat(airpol.g, model=matern, fill.all=T)
		v <- variogram(airpol.g,50)

		airpol.fit = fit.lmc(v, airpol.g, model=matern, 
						  fit.ranges=FALSE, 
						  correct.diagonal=1.01)

		plot(v, model=airpol.fit)

		# Running reconstruction and storing output at "info"
		info <- capture.output(
			timestamp_map_rebuilt <- predict(airpol.fit, newdata = coords)
		)

		timeserie_map[[i]] <- timestamp_map_rebuilt 

		# Formatting console output
		ic <- info[1] # string log for Intrinsic Correlation
		method <- substr(info[2], 8, 25) # string log formatted for cokriging

		# Progress
		progress = ceiling(100*i/length(snapshot_series))
		cat('\r',format(paste0(ic, " ", method, ": ", progress, "% ")))
		flush.console()
	}

	message("\nDone!")
	return(timeserie_map)
}
# ------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------

#Read this csv - ignore the rest (minha alteração)
sp_coords <- read.csv("/home/larissa/Documents/airPolution/environment/spcoords_25x25.csv")

snapshot_series <- grouping_series()

var_name_stations <- var_name_choice(snapshot_series[[1]])
						
#write.table(CO_PM10_03_snapshot_series, 'CO_PM10_03_snapshot_series_teste_texto.txt')

#Precisa converter os data.frames em spatial objects: erro a seguir
#Error in gstat(airpol.g, "PM10", log(unlist(airpol_snapshot$PM10)) ~ 1,  : trying to get slot "proj4string" from an object (class "data.frame") that is not an S4 object 

station_reconst <- predict_series( snapshot_series, var_name_stations, sp_coords)
#-------------------------------------------------------------------------------------

