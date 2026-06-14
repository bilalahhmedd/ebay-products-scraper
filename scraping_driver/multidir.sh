myArray=(

)


triplet_len=${#myArray[@]}

j=0
while [ $j -lt $triplet_len ]
  do
    if mkdir ./${myArray[j]}; then
        cd ./${myArray[j]}
	scrapy crawl ebay -o metadata.csv -a pages=2 -a size=m -a search=${myArray[j]}  #run scrapy crawler inside directory and crawl data
        cd ../ # come back to parent directory
    fi
 ((j++))
 done
