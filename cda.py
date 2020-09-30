import random
import time
import pandas as pd
import numpy as np

class Order:
    def __init__(self, Status, Category, Type, Size, Price, Index, Time):
        self.Status = Status # Add, Cancel, Outstanding, Executed
        self.Category = Category # Market, Limit, and for makrket order, price = 0 or max_price
        self.Type = Type # Bid, Ask
        self.Size = Size # Int
        self.Price = Price
        self.Index = Index 
        self.Time = Time
        self.ID = str(Status)[0]+str(Category)[0]+str(Type)[0]+str(Index)+str(Time)

    def content(self):
        return [self.Status, self.Category, self.Type, self.Size, self.Price, self.Index, self.Time, self.ID]

    def __repr__(self):
        return repr((self.Status, self.Category, self.Type, self.Size, self.Price, self.Index, self.Time))


class Order_pair:
    def __init__(self,order1,order2,price,size,time):
        
        self.Exe_order = order1
        self.Pair_order = order2
        self.Exe_price = price
        self.Exe_size = size
        self.Exe_time = time
        
    def content(self):
        return [self.Exe_order, self.Pair_order, self.Exe_price, self.Exe_size, self.Exe_time]

    def __repr__(self):
        
        return repr((self.Exe_order, self.Pair_order, self.Exe_price, self.Exe_size, self.Exe_time))

def Get_surplus(pool,olist,Traders):
    s = 0
    for neworder in olist:
        pool[neworder.ID] = neworder
        

    B = {}
    A = {}
        
    for idk in list(pool.keys()):

        norder = pool[idk]
        if norder.Type == 'Bid':
            if norder.Price in list(B.keys()):
                B[norder.Price].append(norder.ID)

            else:
                B[norder.Price] = [norder.ID]

        if norder.Type == 'Ask':
            if norder.Price in list(A.keys()):
                A[norder.Price].append(norder.ID)

            else:
                A[norder.Price] = [norder.ID]
                    

    aps = list(A.keys())
    if len(aps) > 0:
        ap = min(aps)

    else:
        ap = 1000
        aps = [1000]


    bps = list(B.keys())
    if len(bps) > 0:
        bp = max(bps)

    else:
        bp = 0
        bps = [0]
    aps.sort()
    bps.sort(reverse = True)
    opB = []
    opA = []
    for bb in bps:
        if bb in B.keys():
            for bo in B[bb]:
                opB.append(pool[bo])
            
    for aa in aps:
        if aa in A.keys():
            for ao in A[aa]:
                opA.append(pool[ao])
            
    lb = len(opB)
    la = len(opA)
    
    if lb*la != 0:
    
        for i in range(min(lb,la)):
            if opB[i].Price >= opA[i].Price:
                id1 = opB[i].Index
                id2 = opA[i].Index

                s += abs(Traders[id1].Valuation - Traders[id2].Valuation)
                #print('s',s,id1,id2,opB[i].Price,Traders[id1].Valuation,opA[i].Price,Traders[id2].Valuation)

            else:
                break
            
    return s


import random
class Trader:
    def __init__(self, index, asset, cash, risk, loss,strategy=[0,0,1]):
        self.Index = index
        self.Asset = asset
        self.Cash = cash
        self.Available_asset = asset
        self.Available_cash = cash
        self.Risk_bear_level = risk
        self.Max_loss = loss
        self.Order_history = []
        self.Outstanding_bid = {}
        self.Outstanding_ask = {}
        self.Outstanding_order = {}
        self.Executed_order = []
        self.Events = []
        self.Surplus = 0
        self.Valuation = 0
        self.Strategy = strategy
        
    def Pool_to_Order(self):
        self.Outstanding_bid = {}
        self.Outstanding_ask = {}
        for ID in list(self.Outstanding_order.keys()):
            order = self.Outstanding_order[ID]
            if order.Type == 'Bid':
                if order.Price in list(self.Outstanding_bid.keys()):
                    self.Outstanding_bid[order.Price].append(order.ID)
                                
                else:
                    self.Outstanding_bid[order.Price] = [order.ID]
                
            if order.Type == 'Ask':
                if order.Price in list(self.Outstanding_ask.keys()):
                    self.Outstanding_ask[order.Price].append(order.ID)
                                
                else:
                    self.Outstanding_ask[order.Price] = [order.ID]
                    
    def Place_Order(self,neworder):
        action = neworder.Status
        if action == 'Cancel':
            print('Trader ',self.Index,' place a ',neworder,neworder.ID)
            if neworder.Type == 'Ask':
                self.Available_asset = self.Asset + neworder.Size
                    
            elif neworder.Type == 'Bid':
                self.Available_cash = self.Cash + (neworder.Size * neworder.Price)
                
            self.Outstanding_bid = {}
            self.Outstanding_ask = {}
            self.Outstanding_order = {}
            return neworder
        
        elif action == 'Add':
        
            neworder.Index = self.Index
            self.Outstanding_order[neworder.ID] = neworder
            print('Trader ',self.Index,' place a ',neworder,neworder.ID)

            if neworder.Category == 'Limit':
                self.Outstanding_order[neworder.ID] = neworder
                if neworder.Type == 'Ask':
                    self.Available_asset = self.Asset - neworder.Size
                    
                elif neworder.Type == 'Bid':
                    self.Available_cash = self.Cash - (neworder.Size * neworder.Price)
            self.Pool_to_Order()
            
            return neworder
        
    def Update(self, order_pair,position):
        if position == 0:
        
            order = order_pair.Exe_order
            
        elif position == 1:
            order = order_pair.Pair_order
            
        ID = order.ID

        self.Outstanding_order[ID].Size -= order_pair.Exe_size
        self.Surplus += abs(self.Valuation-order_pair.Exe_price)*order_pair.Exe_size

        dead_ID = []
        if self.Outstanding_order[ID].Size == 0:
            dead_ID.append(ID)
            
        if order.Type == 'Bid':
            self.Asset += order_pair.Exe_size
            self.Cash -= (order_pair.Exe_price*order_pair.Exe_size)
        
        elif order.Type == 'Ask':
            self.Asset -= order_pair.Exe_size
            self.Cash += (order_pair.Exe_price*order_pair.Exe_size)
            
        if dead_ID != []:
            for d in dead_ID:
                del self.Outstanding_order[d]
                
        self.Pool_to_Order()
        
            
    def Min_Ask_Price(self):
        asks = list(self.Outstanding_ask.keys())
        if asks == []:
            a = 100
        else:
            a = min(asks)
        return a
        
    def Max_Bid_Price(self):
        bids = list(self.Outstanding_bid.keys())
        if bids == []:
            b = 0
        else:
            b = max(bids)
        return b        
    
    def Get_Information(self):
        print('Trader ',self.Index,' holds ',self.Asset,' assets and ',self.Cash,' cash')
        print('It has outstanding orders listed ',self.Outstanding_order)
        print('Available ',self.Available_asset,self.Available_cash)    

import copy
#player_pool = {Index:Trader}

class Market:
    def __init__(self,maxprice):
        self.Order_Pool = {}
        self.Bid_Orders = {}
        self.Ask_Orders = {}
        self.Ask_Price = maxprice
        self.Cap = maxprice
        self.Bottom = 0
        self.Bid_Price = 0
        self.Bid_Dynamics = []
        self.Ask_Dynamics = []
        self.Surplus = 0
        self.Ture_Value = 0

        
                
        
    def Get_Ask_Price(self):
        asks = list(self.Ask_Orders.keys())
        if len(asks) > 0:
            self.Ask_Price = min(asks)
            
        else:
            self.Ask_Price = self.Cap
        
            

        
    def Get_Bid_Price(self):
        bids = list(self.Bid_Orders.keys())
        if len(bids) > 0:
            self.Bid_Price = max(bids)
            
        else:
            self.Bid_Price = self.Bottom
        

        
    def Write_into_Pool(self,order):
        self.Order_Pool[order.ID] = order
        
    def Pool_to_Book(self):
        self.Bid_Orders = {}
        self.Ask_Orders = {}
        
        for ID in list(self.Order_Pool.keys()):
    
            order = self.Order_Pool[ID]
            if order.Type == 'Bid':
                if order.Price in list(self.Bid_Orders.keys()):
                    self.Bid_Orders[order.Price].append(order.ID)
                                
                else:
                    self.Bid_Orders[order.Price] = [order.ID]
                
            if order.Type == 'Ask':
                if order.Price in list(self.Ask_Orders.keys()):
                    self.Ask_Orders[order.Price].append(order.ID)
                                
                else:
                    self.Ask_Orders[order.Price] = [order.ID]
                    
        self.Get_Ask_Price()
        self.Get_Bid_Price()
        
    def Trade(self, order, time):
        trade_result = []
        

        remaining_size = order.Size
        orders = []
        if order.Type == 'Bid':
            optional_price = list(self.Ask_Orders.keys())
            optional_price.sort()
            for p in optional_price:
                if p <= order.Price:
                    orders += self.Ask_Orders[p]
        
        else:
            optional_price = list(self.Bid_Orders.keys())
            optional_price.sort(reverse = True)
            for p in optional_price:
                if p >= order.Price:
                    orders += self.Bid_Orders[p]
                    

        dead_ID = []
        for ID in orders:
            pair = self.Order_Pool[ID]
            order_c = copy.deepcopy(order)
            
            if pair.Size <= remaining_size:
                exe_price = pair.Price
                exe_size = pair.Size
                self.Surplus += abs(order_c.Price-pair.Price)*exe_size
                order_pair = Order_pair(order_c,pair,exe_price,exe_size,time)
                print(order_pair)
                remaining_size -= exe_size
                trade_result.append(order_pair)
                dead_ID.append(ID)
                
            elif pair.Size > remaining_size and remaining_size > 0:
                exe_price = pair.Price
                exe_size = remaining_size
                remaining_size = 0
                pair.Size -= exe_size
                self.Surplus += abs(order_c.Price-pair.Price)*exe_size
                order_pair = Order_pair(order_c,pair,exe_price,exe_size,time)
                print(order_pair)
                trade_result.append(order_pair)
                break
                
            else:
                break
                
        if dead_ID != []:
            for d in dead_ID:
                del self.Order_Pool[d]
                
        if remaining_size > 0:
            order.Size = remaining_size
            self.Write_into_Pool(order)
            #trade_result.append(order)
            
        #elif remaining_size == 0:
            #trade_result.append(0)
            
        return trade_result
        
        
        
    def Update(self,order_o,time):#order_o original order
        order = copy.deepcopy(order_o)
        results = []
        if order != 0:
            if order.Status == 'Add':
                if order.Type == 'Bid':
                    if order.Price < self.Ask_Price:
                        self.Write_into_Pool(order)

                    else:
                        results = self.Trade(order,time)

                if order.Type == 'Ask':
                    if order.Price > self.Bid_Price:
                        self.Write_into_Pool(order)

                    else:
                        results = self.Trade(order,time)
                        
            if order.Status == 'Cancel':
                del self.Order_Pool[order.ID]
                
                
            self.Pool_to_Book()
            
        return results

def Simu(maxprice,midprice,r,itera,mu,sigma,num):
    Traders = {}

    for i in range(1,num+1):
        Traders[i] = Trader(i,1, 1000, 0, 0, [0,0,1])

    
    V = [midprice]
    s = np.random.normal(mu, sigma, itera)
    rs = list(s)
    for ittt in range(itera):
        V.append(0.2*V[ittt] + 0.8*V[0] + rs[ittt])
    tot = 0
    M = Market(maxprice)
    mpool = copy.deepcopy(M.Order_Pool)
    for step in range(itera):
        
        
        
        lists = []
        records = []

        for ii in range(1,num+1):
            #print(M.Order_Pool)
            valuation = int(max(0,min(np.random.normal(V[step],10),maxprice)))
            Traders[ii].Valuation = valuation
            if len(Traders[ii].Outstanding_order.keys()) > 0:
                for outids in Traders[ii].Outstanding_order.keys():
                    cancelorder = copy.deepcopy(Traders[ii].Outstanding_order[outids])
                    cancelorder.Status = 'Cancel'
                    Traders[ii].Place_Order(cancelorder)
                    M.Update(cancelorder,step)
            #print(valuation)
            stra = Traders[ii].Strategy
            bid = M.Bid_Price
            asl = M.Ask_Price
            demand = random.randint(stra[0],stra[1])
            action = random.randint(0,1)

            if action == 0:
                a = 'Ask'
                p = valuation + demand
                s = 1

            else:
                a = 'Bid'
                p = valuation - demand
                s = 1

            order = Order('Add','Limit',a,s,p,ii,step)
            order_c = copy.deepcopy(order)
            lists.append(order_c)
            Traders[ii].Place_Order(order)
            result = M.Update(order,step)
            if result != []:
                for epair in result:
                    a = epair.Exe_order.Index
                    b = epair.Pair_order.Index
                    Traders[a].Update(epair,0)
                    Traders[b].Update(epair,1)

            records += result
            #print(M.Order_Pool)

        oop = copy.deepcopy(lists)
        tot += Get_surplus(mpool,oop,Traders)
        
        

        
        
    asur = 0
    for i in range(1,num+1):
        asur += Traders[i].Surplus

    print(asur)
    print(tot,asur/tot)
    return asur/tot

sr = []
for i in range(10):
    sr.append(Simu(1000,500,0.5,10,0,100,20))

print(np.array(sr).mean())
