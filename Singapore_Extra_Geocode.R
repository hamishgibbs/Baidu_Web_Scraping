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

extra_geo_id = extra_geo %>%
  rename(case_id = caseNo) %>%
  select(case_id)
sing_id = sing %>%
  select(case_id)

combined_geo = rbind(sing_id, extra_geo_id)
unique_ids = unique(combined_geo$case_id)

i = 1
for (id in unique_ids){
  filtered = combined_geo %>%
    filter(case_id == id)
  if (i == 1){
    bbox_df = tibble(id=id, geometry=st_as_sfc(st_bbox(filtered$geometry)))
  }else{
    bbox_df = rbind(bbox_df, tibble(id=id, geometry=st_as_sfc(st_bbox(filtered$geometry))))
  }
  
  i = i + 1
}
bbox_df = st_sf(case_id = bbox_df$id, geometry=bbox_df$geometry)

bbox_df %>%
  ggplot() +
  geom_sf()
leaflet(bbox_df) %>%
  addProviderTiles(providers$CartoDB.Positron) %>%
  addPolygons(color = "#444444", weight = 1, smoothFactor = 0.5,
              opacity = 1.0, fillOpacity = 0.5,
              fillColor = ~pal(case_id))
  
  