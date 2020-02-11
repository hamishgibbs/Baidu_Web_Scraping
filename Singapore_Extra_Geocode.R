pacman::p_load(jsonlite, 
               tidyverse,
               dplyr,
               geojsonio,
               leaflet,
               rgdal,
               broom,
               sf,
               viridis)

extra_geo <- st_as_sf(geojson_read("/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_additional_geodata.geojson",  what = "sp"))


leaflet(sf) %>% 
  addProviderTiles(providers$CartoDB.Positron) %>%
  addCircleMarkers(radius=4, 
                   color = ~pal(caseNo),
                   stroke = FALSE,
                   fillOpacity = 1,
                   popup = paste("Case ID", sf$caseNo, "<br>",
                                 "Text Address:", sf$text_orig, "<br>",
                                 "Visit Type:", sf$type, "<br>"),
                   clusterOptions = markerClusterOptions())

sing = st_as_sf(geojson_read('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data_id.geojson', what = "sp"))
sing
pal <- colorNumeric(
  palette = "YlGnBu",
  domain = sing$case_id
)

leaflet(sing) %>%
  addProviderTiles(providers$CartoDB.Positron) %>%
  addCircleMarkers(radius=4, 
                   color = ~pal(case_id),
                   stroke = 1,
                   fillOpacity = 0, 
                   popup = paste("Case ID", sing$case_id, "<br>",
                                 "Age:", sing$age, "<br>",
                                 "Gender:", sing$gender, "<br>",
                                 "From:", sing$from, "<br>",
                                 "Citizenship:", sing$citizenship, "<br>")) %>%
  addCircleMarkers(lng = st_coordinates(extra_geo)[,1],
                   lat = st_coordinates(extra_geo)[,2],
                   radius=4, 
                   color = ~pal(extra_geo$caseNo),
                   stroke = FALSE,
                   fillOpacity = 1,
                   popup = paste("Case ID", extra_geo$caseNo, "<br>",
                                 "Text Address:", extra_geo$text_orig, "<br>",
                                 "Visit Type:", extra_geo$type, "<br>"),
                   markerClusterOptions())

#make boundig boxes around extant of each traveller





clusterOptions = markerClusterOptions()
c(st_coordinates(extra_geo)[,1])
pal
pal(sf$caseNo)
