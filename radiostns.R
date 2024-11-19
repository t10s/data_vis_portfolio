library(tidyverse)

#read data
stat_stns <- read.csv("state_stations.csv")
stn_info <- read.csv("station_info.csv")
stn_contour <- read.csv("FM_service_contour_current.txt", sep = "|")
stn_contour <- stn_contour %>% mutate(across(where(is.character), str_trim))
fmq <- read.csv("fmq", sep = "|", header = FALSE)
fmq_slim <- select(fmq, c(2,38,39))
fmq_slim <- fmq_slim %>% mutate(across(where(is.character), str_trim)) #remove whitespace from char type
colnames(fmq_slim)[1] <- "call_sign"
colnames(fmq_slim)[2] <- "application_id"
colnames(fmq_slim)[3] <- "lms_application_id"

#cross ref datasets
stn_contour_xref_full <- merge(fmq_slim, stn_contour, by = "application_id") %>% 
  filter(call_sign != "-           ") %>%
  select(-c(1,3,4,5,6))

map <- map_data("state")


#join dfs
stn_info_all <- inner_join(stat_stns, stn_info, by = "call_sign")
religious <- c("Religious", "Christian", "Gospel", "gospel", "Worship", "worship")
classical <- c("Classical", "classical")
sports <- c("Sports", "sports")
pop_rock <- c("pop", "Pop", "Rock", "rock", "hits", "Hits", "top", "Top", "mainstream", "Mainstream")
news <- c("News", "news")

#group stns and remove nas
stn_info_all <- stn_info_all %>%  mutate(type = case_when(str_detect(format, paste0(religious, collapse = "|")) ~ "Religious/Gospel",
                                                          str_detect(format, paste0(classical, collapse = "|")) ~ "Classical",
                                                          str_detect(format, paste0(sports, collapse = "|")) ~ "Sports",
                                                          str_detect(format, paste0(pop_rock, collapse = "|")) ~ "Rock/Pop/Mainstream",
                                                          str_detect(format, paste0(news, collapse = "|")) ~ "News")) %>%
  na.omit(type)


#join all coordinates with station type data and select relevant cols
q_full <- right_join(stn_contour_xref_full, stn_info_all, by = "call_sign")
q_full_slim <- q_full %>% select(-c(363:374))

#pivot longer and split lat long for service contour data
q_full_long <- q_full_slim %>% pivot_longer(cols = c(2:362))

q_full_cont <- q_full_long %>%
  filter(name != "transmitter_site") %>%
  select(c(1,2,4)) %>%
  mutate(value = str_sub(value, 1,-1)) %>%
  separate(value, into = c("lat", "long"), sep = ",")
  
q_full_cont$lat <- as.numeric(q_full_cont$lat)
q_full_cont$long <- as.numeric(q_full_cont$long)
q_full_cont <- q_full_cont %>% filter(long >= -130)
q_full_cont$group <- rep(c(1:1758), each = 360)



#filter and split data for transmitter sites
q_full_trsit <- q_full_long %>%
  filter(name == "transmitter_site") %>%
  select(c(1,2,4)) %>%
  mutate(value = str_sub(value, 1,-1)) %>%
  separate(value, into = c("lat", "long"), sep = ",")

q_full_trsit$lat <- as.numeric(q_full_trsit$lat)
q_full_trsit$long <- as.numeric(q_full_trsit$long)
q_full_trsit <- q_full_trsit %>% filter(long >= -130)



p <- ggplot() +
  geom_polygon(data = map, aes(x=long, y=lat, group=group), col = "white", alpha = 0) +
  coord_map() +
  geom_path(data = q_full_cont, aes(x=long, y=lat, colour = type, group = group), alpha = .5) +
  geom_point(data = q_full_trsit, aes(x=long, y=lat, colour = type), alpha = .3) +
  theme_void() +
  theme(plot.background = element_rect(colour = "black", fill = "black"),
        legend.text = element_text(colour = "white", size = 13)) +
  ggtitle("FM Radio Stations in the USA with Service Contours") +
  labs(subtitle = "Categories based on keywords occurung in station format",
       caption = "Data from TidyTuesday 08th Nov 2022 Dataset and from FCC Website") +
  theme(plot.title = element_text(hjust = .5, colour = "white"),
        plot.subtitle = element_text(hjust = .5, colour = "white"),
        plot.caption = element_text(hjust = 0, colour = "white"))


ggsave('radio_stns.png', plot=p, width=20, height=11)


