
data = read_rds('/Users/hamishgibbs/Dropbox/nCov-2019/data_sources/mobility_data/china_prf_connectivity.rds')

data

connect = read_rds('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Connectivity/connectivity_draft.rds')
connect

image(connect)
matrix(connect)
connect %>%
  select(-date, -from)

image(matrix(connect$`110100`))

image(matrix(connect[,3:length(connect)]))

image(as.matrix(connect[,3:length(connect)]), col=rainbow(100))
rainbow(100)


shp = read_rds('/Users/hamishgibbs/Dropbox/nCov-2019/data_sources/demographic_data/shp_pop.rds')

shp = as_tibble(shp) %>%
  select(-geometry)
shp
write_csv(shp, '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Unique_URLs/shp_pop.csv')
