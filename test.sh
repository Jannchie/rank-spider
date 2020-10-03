kill -9 $(ps -ef|grep hot-search.py|gawk '$0 !~/grep/ {print $2}' |tr -s '\n' ' ')
cd ~/zhihu-spider
git pull --force
nohup python3 ./src/weibo/hot-search.py &
nohup python3 ./src/zhihu/hot-search.py &