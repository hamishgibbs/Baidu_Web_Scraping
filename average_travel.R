pop = read_rds('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Connectivity/shp_pop.rds')
pop

data = read_rds('/Users/hamishgibbs/Dropbox/nCov-2019/data_sources/mobility_data/china_prf_connectivity.rds')
data

wuhan_code = as.character(pop[pop$PYNAME == 'Wuhan Shi', 'CNTY_CODE'])[1]

for (i in 1:length(data$date)){
  current_date = data$date[i]
  
  date_data = data[data$date == current_date,'data'][[1]][[1]]
  
  if (i == 1){
    date_destinations = as.tibble(date_data[wuhan_code,]) %>%
      mutate(date = current_date) %>%
      mutate(location = colnames(date_data))
  } else {
    dd_tmp = as.tibble(date_data[wuhan_code,]) %>%
      mutate(date = current_date) %>%
      mutate(location = colnames(date_data))
      
    date_destinations = rbind(date_destinations, dd_tmp)
  }
  
}

average_flow = date_destinations %>%
  group_by(location) %>%
  summarize(average_flow = mean(value, na.rm=TRUE))
average_flow
plot(average_flow$average_flow)

