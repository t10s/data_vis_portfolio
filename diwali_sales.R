# tidy tuesday for 14th november - diwali sales

# load packages
library(tidyverse)
library(sf)
library(ggimage)


# read in the data
data <- readr::read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2023/2023-11-14/diwali_sales_data.csv')
ind <- read_sf("IND_adm1.shp") # data from diva-gis
# have a look at the shapefile
ggplot(ind) +
  geom_sf() 


# aggregate fireworks data
data_st <- data %>%
  na.omit() %>%
  group_by(State) %>%
  summarise(totamt = sum(Amount))

# select cols from shpfile
india <- ind %>%
  select(ID_0, NAME_0, ID_1, NAME_1, geometry)


# join
map_data <- full_join(data_st, india, by=c("State"="NAME_1")) # full join to include missing
map_data <- map_data %>% filter(State != "Uttarakhand") # no shape data for uttarakhand
map_data <- map_data %>% mutate("Amount in Lakhs" = round(totamt / 100000, 2))
map_data <- st_as_sf(map_data) # to avoid this step do spatial data as first arg in join

imagel <- image_read2("diya.png")
imager <- image_read2("fireworks.png")

# map data
ggplot(map_data) +
  geom_sf(aes(fill=`Amount in Lakhs`)) +
  theme_void() +
  scale_fill_continuous(low="yellow", high="orange") +
  theme(legend.direction = "horizontal",
        legend.position = c(0.8, 0.45),
        legend.title = element_blank(),
        plot.title = element_text(size=20, hjust=.5, face = "bold")) +
  labs(title = "Diwali Spending per State") +
  annotate("text", x=93, y=20, label="Amount in Lakh ₹") +
  annotate("text", x=81.5, y=4, label="Data:https://github.com/rfordatascience/tidytuesday/tree/master/data/2023/2023-11-14",
           fontface=2, colour="grey49", size=3) +
  annotate("text", x=70.5, y=5, label="Grey Areas = No Data",
           fontface=1, colour="black", size=3) +
  annotation_custom(rasterGrob(imagel), xmin = 65, xmax = 74.5, ymin = 30, ymax = 35) +
  annotation_custom(rasterGrob(imager), xmin = 80, xmax = 95, ymin = 29, ymax = 37) +
  annotate("text", x=80, y=7, label="stingh@mstdn.party",
           fontface=2, colour="grey86", size=5) 

ggsave("diwali-sales.jpg", plot = last_plot())




