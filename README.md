# RedditDialogue
-------

## Downloading the Reddit Dumps

You would first need to download the Reddit Dumps for comments and posts from 
https://www.reddit.com/r/datasets/comments/3bxlg7/i_have_every_publicly_available_reddit_comment/

Thanks to /u/Stuck_In_the_Matrix for gathering all these data together. https://www.reddit.com/user/Stuck_In_the_Matrix

## How to run

* Create a data folder
* Put RS and RC file pairs for same months
* To generate train and test dialogues you can use something like following

```bash
python reader.py --file_tag 2017-03 --output_folder sample_data/train --n_posts 500
python reader.py --file_tag 2011-03 --output_folder sample_data/test --n_posts 500
```

## Sample data

Sample data folder contains dialogues extracted from following two files.

* 'train' from 2017-03
* 'test' from 2011-03
