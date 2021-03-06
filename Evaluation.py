{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Class to calculate precision and recall\n",
    "\n",
    "import random\n",
    "\n",
    "class precision_recall_calculator():\n",
    "    \n",
    "    def __init__(self, test_data, train_data, pm, is_model):\n",
    "        self.test_data = test_data\n",
    "        self.train_data = train_data\n",
    "        self.user_test_sample = None\n",
    "        self.model1 = pm\n",
    "        self.model2 = is_model\n",
    "        \n",
    "        self.ism_training_dict = dict()\n",
    "        self.pm_training_dict = dict()\n",
    "        self.test_dict = dict()\n",
    "    \n",
    "    #Method to return random percentage of values from a list\n",
    "    def remove_percentage(self, list_a, percentage):\n",
    "        k = int(len(list_a) * percentage)\n",
    "        random.seed(0)\n",
    "        indicies = random.sample(range(len(list_a)), k)\n",
    "        new_list = [list_a[i] for i in indicies]\n",
    "    \n",
    "        return new_list\n",
    "    \n",
    "    #Create a test sample of users for use in calculating precision\n",
    "    #and recall\n",
    "    def create_user_test_sample(self, percentage):\n",
    "        #Find users common between training and test set\n",
    "        users_test_and_training = list(set(self.test_data['user_id'].unique()).intersection(set(self.train_data['user_id'].unique())))\n",
    "        print(\"Length of user_test_and_training:%d\" % len(users_test_and_training))\n",
    "\n",
    "        #Take only random user_sample of users for evaluations\n",
    "        self.users_test_sample = self.remove_percentage(users_test_and_training, percentage)\n",
    "\n",
    "        print(\"Length of user sample:%d\" % len(self.users_test_sample))\n",
    "        \n",
    "    #Method to generate recommendations for users in the user test sample\n",
    "    def get_test_sample_recommendations(self):\n",
    "        #For these test_sample users, get top 10 recommendations from training set\n",
    "        #self.ism_training_dict = {}\n",
    "        #self.pm_training_dict = {}\n",
    "\n",
    "        #self.test_dict = {}\n",
    "\n",
    "        for user_id in self.users_test_sample:\n",
    "            #Get items for user_id from item similarity model\n",
    "            print(\"Getting recommendations for user:%s\" % user_id)\n",
    "            user_sim_items = self.model2.recommend(user_id)\n",
    "            self.ism_training_dict[user_id] = list(user_sim_items[\"song\"])\n",
    "    \n",
    "            #Get items for user_id from popularity model\n",
    "            user_sim_items = self.model1.recommend(user_id)\n",
    "            self.pm_training_dict[user_id] = list(user_sim_items[\"song\"])\n",
    "    \n",
    "            #Get items for user_id from test_data\n",
    "            test_data_user = self.test_data[self.test_data['user_id'] == user_id]\n",
    "            self.test_dict[user_id] = set(test_data_user['song'].unique() )\n",
    "    \n",
    "    #Method to calculate the precision and recall measures\n",
    "    def calculate_precision_recall(self):\n",
    "        #Create cutoff list for precision and recall calculation\n",
    "        cutoff_list = list(range(1,11))\n",
    "\n",
    "\n",
    "        #For each distinct cutoff:\n",
    "        #    1. For each distinct user, calculate precision and recall.\n",
    "        #    2. Calculate average precision and recall.\n",
    "\n",
    "        ism_avg_precision_list = []\n",
    "        ism_avg_recall_list = []\n",
    "        pm_avg_precision_list = []\n",
    "        pm_avg_recall_list = []\n",
    "\n",
    "\n",
    "        num_users_sample = len(self.users_test_sample)\n",
    "        for N in cutoff_list:\n",
    "            ism_sum_precision = 0\n",
    "            ism_sum_recall = 0\n",
    "            pm_sum_precision = 0\n",
    "            pm_sum_recall = 0\n",
    "            ism_avg_precision = 0\n",
    "            ism_avg_recall = 0\n",
    "            pm_avg_precision = 0\n",
    "            pm_avg_recall = 0\n",
    "\n",
    "            for user_id in self.users_test_sample:\n",
    "                ism_hitset = self.test_dict[user_id].intersection(set(self.ism_training_dict[user_id][0:N]))\n",
    "                pm_hitset = self.test_dict[user_id].intersection(set(self.pm_training_dict[user_id][0:N]))\n",
    "                testset = self.test_dict[user_id]\n",
    "        \n",
    "                pm_sum_precision += float(len(pm_hitset))/float(N)\n",
    "                pm_sum_recall += float(len(pm_hitset))/float(len(testset))\n",
    "\n",
    "                ism_sum_precision += float(len(ism_hitset))/float(len(testset))\n",
    "                ism_sum_recall += float(len(ism_hitset))/float(N)\n",
    "        \n",
    "            pm_avg_precision = pm_sum_precision/float(num_users_sample)\n",
    "            pm_avg_recall = pm_sum_recall/float(num_users_sample)\n",
    "    \n",
    "            ism_avg_precision = ism_sum_precision/float(num_users_sample)\n",
    "            ism_avg_recall = ism_sum_recall/float(num_users_sample)\n",
    "\n",
    "            ism_avg_precision_list.append(ism_avg_precision)\n",
    "            ism_avg_recall_list.append(ism_avg_recall)\n",
    "    \n",
    "            pm_avg_precision_list.append(pm_avg_precision)\n",
    "            pm_avg_recall_list.append(pm_avg_recall)\n",
    "            \n",
    "        return (pm_avg_precision_list, pm_avg_recall_list, ism_avg_precision_list, ism_avg_recall_list)\n",
    "     \n",
    "\n",
    "    #A wrapper method to calculate all the evaluation measures\n",
    "    def calculate_measures(self, percentage):\n",
    "        #Create a test sample of users\n",
    "        self.create_user_test_sample(percentage)\n",
    "        \n",
    "        #Generate recommendations for the test sample users\n",
    "        self.get_test_sample_recommendations()\n",
    "        \n",
    "        #Calculate precision and recall at different cutoff values\n",
    "        #for popularity mode (pm) as well as item similarity model (ism)\n",
    "        \n",
    "        return self.calculate_precision_recall()\n",
    "        #return (pm_avg_precision_list, pm_avg_recall_list, ism_avg_precision_list, ism_avg_recall_list)    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
