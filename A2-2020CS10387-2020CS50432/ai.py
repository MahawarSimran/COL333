
from cmath import inf
import time
import random
import numpy as np
from typing import List, Tuple, Dict
from connect4.utils import get_pts, get_valid_actions, Integer

class Node:
    def __init__(self, state, player_number):
        self.player = player_number
        self.state = state
        self.action=None
    def make_move(self,column, is_popout):
        
        board, temp = self.state
        m = board.shape[0]
        n = board.shape[1]
        aa = np.zeros((m,n))
        i =0
        while(i < m):
            for j in range(n):
                aa[i][j] = board[i][j]
            i +=1
        i =0
        if(is_popout):
            while(i<m-1):
                aa[i+1][column] = board[i][column]
                i+=1
            aa[0][column] =0
        else:
            i =m-1
            while(i>=0):
                if(aa[i][column] == 0):
                    aa[i][column] = self.player
                    break
                i -= 1
        return aa
    def make_child(self,column,is_popout):
        board , popout = self.state
        leftpopout=dict()
        leftpopout[self.player]= Integer(popout[self.player]._i-1)
        nextplayer=1
        if(self.player==1):
            nextplayer=2
            leftpopout[2]=Integer(popout[2]._i)
        else:
            leftpopout[1]=Integer(popout[1]._i)
        u=Node((self.make_move(column,is_popout),leftpopout),nextplayer)
        return u
class AIPlayer:
    def __init__(self, player_number: int, time: int):
        """
        :param player_number: Current player number
        :param time: Time per move (seconds)
        """
        self.player_number = player_number
        self.type = 'ai'
        self.player_string = 'Player {}:ai'.format(player_number)
        self.time = time
        # Do the rest of your implementation here

    def minmax(self,node,depth,alpha,beta,max_depth):
        # print("Alpha: ",alpha)
        # print("Beta: ",beta)
        opposite=1
        if(self.player_number==1):
            opposite=2
        CurrState=node.state
        board,popouts=node.state
        if(depth==max_depth):
            score=get_pts(self.player_number,board)-get_pts(opposite,board)
            return score
        
        if(self.player_number==node.player):
            bestscore=-inf
            AllowedMoves=get_valid_actions(node.player,CurrState)
            if len(AllowedMoves)==0 :
                score=get_pts(self.player_number,board)-get_pts(opposite,board)
                return score
            for (col,isPop) in AllowedMoves:
                child=node.make_child(col,isPop)
                score=self.minmax(child,depth+1,alpha,beta,max_depth)
                if (score>bestscore):
                    node.action=(col,isPop)
                bestscore=max(bestscore,score)
                alpha=max(alpha,bestscore)
                if beta<=alpha:
                    break
            return bestscore

            # Code for max player

        else:
            bestscore=+inf
            AllowedMoves=get_valid_actions(node.player,CurrState)
            if len(AllowedMoves)==0 :
                score=get_pts(self.player_number,board)-get_pts(opposite,board)
                return score
            for (col,isPop) in AllowedMoves:
                child=node.make_child(col,isPop)
                score=self.minmax(child,depth+1,alpha,beta,max_depth)
                if (score<bestscore):
                    node.action=(col,isPop)
                bestscore=min(bestscore,score)
                beta=min(beta,bestscore)
                if beta<=alpha:
                    break
            return bestscore

    def expectimax(self,node,depth,max_depth):
        opposite=1
        if(self.player_number==1):
            opposite=2
        CurrState=node.state
        board,popouts=node.state
        if(depth==max_depth):
            score=get_pts(self.player_number,board)-get_pts(opposite,board)
            return score
        
        if(self.player_number==node.player):
            bestscore=-inf
            AllowedMoves=get_valid_actions(node.player,CurrState)
            if len(AllowedMoves)==0 :
                score=get_pts(self.player_number,board)-get_pts(opposite,board)
                return score
            for (col,isPop) in AllowedMoves:
                child=node.make_child(col,isPop)
                score=self.expectimax(child,depth+1,max_depth)
                if (score>bestscore):
                    node.action=(col,isPop)
                bestscore=max(bestscore,score)
  
            return bestscore

            # Code for max player

        else:
            bestscore=-inf
            AllowedMoves=get_valid_actions(node.player,CurrState)
            if len(AllowedMoves)==0 :
                score=get_pts(self.player_number,board)-get_pts(opposite,board)
                return score
            total =0
            number = 0
            for (col,isPop) in AllowedMoves:
                child=node.make_child(col,isPop)
                score=self.expectimax(child,depth+1,max_depth)
                if (score<bestscore):
                    node.action=(col,isPop)
                total += score
                number += 1
            bestscore = total/number
            return bestscore


    def get_intelligent_move(self, state: Tuple[np.array, Dict[int, Integer]]) -> Tuple[int, bool]:
        Maxdepth=5
        opposite=1
        if(self.player_number==1):
            opposite=2
        AllowedMoves2=get_valid_actions(opposite,state)
        choice2=len(AllowedMoves2)
        AllowedMoves1=get_valid_actions(self.player_number,state)
        choice1=len(AllowedMoves1)
        choice=max(choice1,choice2)
        if choice==1:
            Maxdepth=12
        elif choice==2:
            Maxdepth=11
        elif choice==3:
            Maxdepth=10
            if self.time>12:
               Maxdepth=11
        elif choice==4:
            Maxdepth=7
            if self.time>10:
                Maxdepth=8
        elif choice==5:
            Maxdepth=6
            if self.time>16:
                Maxdepth=8
            elif self.time>8:
                Maxdepth=7
        # elif choice==6:
        #     Maxdepth=6
        #     if self.time>16:
        #         Maxdepth=8
        #     elif self.time>10:
        #         Maxdepth=7
        # elif choice==7:
        #     Maxdepth=6
        #     if self.time>18:
        #         Maxdepth=8
        #     elif self.time>12:
        #         Maxdepth=7
        # elif choice==8:
        #     Maxdepth=5
        #     if self.time>16:
        #         Maxdepth=7
        #     elif self.time>11:
        #         Maxdepth=6
        if choice<9 and choice>5:
            Maxdepth=6
            if self.time>18:
                Maxdepth=8
            elif self.time>12:
                Maxdepth=7
        elif choice>8 and choice<12:
            Maxdepth=4
            if self.time>15:
                Maxdepth=6
            elif self.time>10:
                Maxdepth=5
        
        elif choice>11 and choice<14:
            Maxdepth=4
        elif choice>13:
            Maxdepth=3
            if self.time>12:
                Maxdepth=4
       
        print("Choices: ",str(choice))
        print("Depth: ",str(Maxdepth)) 
        t1=time.time()
        root=Node(state,self.player_number)
        self.minmax(root,0,-inf,inf,Maxdepth)
        t2=time.time()
        exec_time=t2-t1
        print(self.player_string+" Time Taken:"+ str(exec_time))
        print("Popout left:" + str(state[1][self.player_number]._i))
        
        return root.action
        # Minmax with purning
      
    def get_expectimax_move(self, state: Tuple[np.array, Dict[int, Integer]]) -> Tuple[int, bool]:
        Maxdepth=4
        t1=time.time()
        opposite=1
        if(self.player_number==1):
            opposite=2
        AllowedMoves2=get_valid_actions(opposite,state)
        choice2=len(AllowedMoves2)
        AllowedMoves1=get_valid_actions(self.player_number,state)
        choice1=len(AllowedMoves1)
        choice=max(choice1,choice2)

        if choice>13:
            Maxdepth=3
        elif choice>11:
            Maxdepth=3
            if self.time>16:
                Maxdepth=4
        elif choice>6:
            Maxdepth=4
        elif choice>4:
            Maxdepth=5
        elif choice>2:
            Maxdepth=6
            if self.time>12:
                Maxdepth=7
        else:
            Maxdepth=8
        
        # elif choice>
        print("Choices: ",str(choice))
        print("Depth: ",str(Maxdepth)) 
        root=Node(state,self.player_number)
        self.expectimax(root,0,Maxdepth)
        t2=time.time()
        exec_time=t2-t1
        print(self.player_string+ " Time Taken:"+ str(exec_time))
        print("Popout left:" + str(state[1][self.player_number]._i))
        return root.action
