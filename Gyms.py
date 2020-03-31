import matplotlib.pyplot as plt
import numpy as np

class Gym(object):
    """
    """
    def __init__(self, epsilon=0.5):
        self.epsilon = epsilon

class ForwardTDLambdaGym(Gym):
    """
    A Gym to Train an Agent in the TDLambda Method
    Assumes that the agent has the following functions implemented for training
    Agent:
        agent.learn(X_train, y_train)
        agent.play(state, real_epsilon)
        agent.decay_rate
        agent.create_q_vector(state, action)
        
    For testing requires 
        agent.play(state, real_epsilon)


    """
    def __init__(self, epsilon=0.5, lamb=27):
        """
        Default is TD(inf) because max turns is 27
        """
        Gym.__init__(self, epsilon)
        self.lamb = lamb

    def simulate(self, agent, env, opponent_1, opponent_2, episodes=10000, show_every = 1000, training = True):
        """
        Simulate episodes -
               Across training we also aggregate statistics across the rolling window of show_every and display with a graph after training
               In this system assuming there are no draws and the rewards for loss and win is equal we get Win % = ((Avg + 5)*10)%
        If Training is True:
            Loops through each episode and creates a dataset of [q_vector, qlambda value experienced]
            After every episode we deploy the dataset as (X_train, y_train) to agents learn function

        If Training is False:
            
        """
        aggr_ep_rewards = {'ep': [], 'avg': [], 'min': [], 'max': [] }
        rewardlist = []


        for n in range(episodes):
            print(f"Episode {n}")
            if n %show_every == 0:
                flag = True
            else:
                flag = False

            state = env.reset(opponent_1, opponent_2)
            done = False
            total_rewards = 0
            turn = 0
            while not done:
                turn += 1
                action = agent.play(state, self.epsilon_scheduler(n, training))
                new_state, rewards, done = env.step(action)
                total_rewards += rewards
                if training:
                    self.update_dataset(agent, state, action, rewards, turn, agent.decay_rate)
                state = new_state
            if training:
                X_train, y_train = self.deploy_dataset()
                agent.learn(X_train, y_train)
                self.clear_dataset()
            rewardlist.append(total_rewards)
            if flag:
                aggr_ep_rewards['ep'].append(n)
                if len(rewardlist) > 0:
                    aggr_ep_rewards['avg'].append(sum(rewardlist)/len(rewardlist))
                    aggr_ep_rewards['min'].append(min(rewardlist))
                    aggr_ep_rewards['max'].append(max(rewardlist))
                rewardlist.clear()

        print("Win Ratio is (AVG+5)/10")
        input()
        plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['avg'], label = 'avg')
        plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['min'], label = 'min')
        plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['max'], label = 'max')
        plt.legend()
        plt.show()
        
        return

    def epsilon_scheduler(self, episodes, training = True):
        """
        Return a lower epsilon as episdoes go higher
        """
        if not training:
            return 0.0
        return self.epsilon / ((episodes+1)**0.125)

    def update_dataset(self, agent, state, action, reward, turn, decay):
        """
        Create an update a dataset in the form  -
        dataset : [[q_vector, actual_reward], [q_vector, actual_reward]....]
        """
        if turn == 1:
            self.dataset = []
        q_vector = agent.create_q_vector(state, action)
        for n in range(len(self.dataset)):
            turn_added = n+1
            turn_diff = turn - turn_added
            if (turn_diff > self.lamb + 1):
                self.dataset[n][1] = self.dataset[n][1] + (decay**turn_diff)*reward
            else:
                pass
        self.dataset.append([q_vector, reward])
        return
    
    def deploy_dataset(self):
        """
        Returns the dataset split into two numpy ndarrays - X_train which has all the input vectors and y_train which has all the experienced values.
        """
        X_train = []
        y_train = []
        for X, y in self.dataset:
            X_train.append(X)
            y_train.append(y)

        return np.asarray(X_train), np.asarray(y_train)

    def clear_dataset(self):
        """
        Reset the dataset
        """
        self.dataset = None

