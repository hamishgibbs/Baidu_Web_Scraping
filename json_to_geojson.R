pacman::p_load(jsonlite, 
               tidyverse,
               dplyr,
               geojsonio,
               leaflet,
               geojson_sf,
               rgdal,
               broom,
               sf)

data = read_json('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data.json')

data

geojson_list(data)
file_to_geojson('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data.json')


geojson_json(data)
geojson_json(data, lat = 'lat', lon = 'lng')

cbndata = read_rds('/Users/hamishgibbs/Dropbox/nCov-2019/data_sources/case_data/CBNDATA_Scrape/cbndata_features.rds')
cbndata %>%
  leaflet() %>% 
  addTiles() %>%
  addCircleMarkers(radius=2, 
                   color = 'k',
                   stroke = FALSE,
                   fillOpacity = 1)

leaflet(data = quakes[1:4,]) %>% addTiles() %>%
  addMarkers(~long, ~lat, icon = greenLeafIcon)
cd_json = geojson_json(case_data)
write_json(cd_json, '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/CDNDATA/case_data.geojson')

st_write(case_data, '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/CDNDATA/cbndata_features.shp')

geojson_sf('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data.geojson')

sf <- geojson_sf(system.file("/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data.geojson", package = "geojsonsf"))

spdf <- geojson_read("/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data.geojson",  what = "sp")
spdf
sf = st_as_sf(spdf)
sf %>%
  ggplot() +
  geom_sf()

write_rds(sf, '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data.rds')

sing = read_rds('/Users/hamishgibbs/Dropbox/nCov-2019/data_sources/case_data/Singapore_Scrape/singapore_data.rds')








