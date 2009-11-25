-module(prjT).

-export([cs/0,ctrand/5,node_tell/5,node_rec/5,start/2,close/1,status/2,stats/1,print/1,move/3,checkgame/1,play/4,mergeMoves/2,checkExists/2,set_random_seed/5,mutate/2]).

cs()->
  spawn(prjT, ctrand, [0,0,0,0,0]),
  spawn(prjT, ctrand, [0,0,0,0,0]).



ctrand(T,L,M,M1,G) ->
  %%%random:seed(now()),
  R = random:uniform(),
  if 
    T > 100000 ->
      io:format("~p: ~p ~p ~p ~p~n", [T,L,M,M1,G]),
      io:format("~p: ~p ~p ~p ~p~n", [T,L/T,M/T,M1/T,G/T]);
    R < 0.25 ->
      ctrand(T+1,L+1,M,M1,G);
    R < 0.5 ->
      ctrand(T+1,L,M+1,M1,G);
    R < 0.75 ->
      ctrand(T+1,L,M,M1+1,G);
    true ->
      ctrand(T+1,L,M,M1,G+1)
  end.

getRand(MYNUM,NUMNODES) ->
  %%%random:seed(now()),
  RANDNUM = random:uniform(NUMNODES),
  if
    RANDNUM == MYNUM ->
      getRand(MYNUM,NUMNODES);
    true ->
      "node" ++ integer_to_list(RANDNUM)
  end.

node_tell(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) ->
    if 
      STATUS == "KnowAndTell" ->
          %%%if know pick random node and tell it the msg
          MSGNODE = getRand(MYNUM,NUMNODES),
          %%%io:format("~p Telling ~p~n", [self(),MSGNODE]),
          list_to_atom(MSGNODE) ! {self(),MYMOVES,{WIN,DRAW,LOSS,ALL}},
          node_rec(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) ;
      true ->
          node_rec(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) 
    end.
  
node_rec(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) ->
     receive
        close ->
           io:format("Stoping ~p~n", [self()]);
        {status,NODE_ID} ->
            %%%if STATUS /= "DontTell" -> 
             %%% io:format("~p | ~p | ~p~n", [MYNUM,STATUS,{WIN,DRAW,LOSS,ALL}]),
            %%%  node_rec(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
            %%%true ->
            %%%  node_rec(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL})
            %%%end;
            NODE_ID ! {MYNUM,STATUS,WIN,DRAW,LOSS,ALL},
            node_rec(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
        stats ->
            %%%io:format("~n~p~n~p~n~p~n~p~n~p", [MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}]),
            
            {ok, WriteDescr} = file:open(test.erl, [append]),
            io:fwrite(WriteDescr, "~n~p).~n%%%~p~n~p~n~p~n~p", [MYMOVES,MYNUM,STATUS,NUMNODES,{WIN,DRAW,LOSS,ALL}]),
            file:close(WriteDescr),

            node_rec(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
        {{NEWWIN,NEWDRAW,NEWLOSS,NEWALL},MYNEWMOVES} ->
          if 
            NEWLOSS > 0 ->
              node_rec(MYNUM,"DontTell",NUMNODES,MYNEWMOVES,{0,0,0,NEWALL});
            NEWWIN + NEWDRAW > 1000 ->
              io:format("DRAWS! ~p | ~p | ~p~n", [MYNUM,STATUS,{NEWWIN,NEWDRAW,NEWLOSS,NEWALL}]),
              node_rec(MYNUM,"KnowDontTell",NUMNODES,MYNEWMOVES,{NEWWIN,NEWDRAW,NEWLOSS,NEWALL});
            true ->
              node_rec(MYNUM,STATUS,NUMNODES,MYNEWMOVES,{NEWWIN,NEWDRAW,NEWLOSS,NEWALL})
          end;
        {NODE_ID,THEIRMOVES,{THEIRWIN,THEIRDRAW,THEIRLOSS,THEIRALL}} ->
            {WINNER,THEIRNEWMOVES,MYNEWMOVES} = play([s,s,s,s,s,s,s,s,s],x,THEIRMOVES,MYMOVES),
            if 
              WINNER == x ->
                NODE_ID ! {{THEIRWIN+1,THEIRDRAW,THEIRLOSS,THEIRALL+1},THEIRNEWMOVES},
                node_rec(MYNUM,"DontTell",NUMNODES,mergeMoves(lists:ukeysort(1,THEIRNEWMOVES ++ MYNEWMOVES),[]),{WIN,DRAW,LOSS+1,ALL+1});
              WINNER == o ->
                NODE_ID ! {{0,0,0,THEIRALL+1},mergeMoves(lists:ukeysort(1,MYNEWMOVES ++ THEIRNEWMOVES),[])},
                %%%if 
                %%%  WIN > 0 ->
                node_rec(MYNUM,"KnowAndTell",NUMNODES,MYNEWMOVES,{WIN+1,DRAW,LOSS,ALL+1});
                %%%  true ->
                %%%   node_rec(MYNUM,STATUS,NUMNODES,MYNEWMOVES,{WIN+1,DRAW,LOSS,ALL+1})
                %%% end;
              true ->
                NODE_ID !  {{THEIRWIN,THEIRDRAW+1,THEIRLOSS,THEIRALL+1},THEIRNEWMOVES},
                node_rec(MYNUM,STATUS,NUMNODES,MYNEWMOVES,{WIN,DRAW+1,LOSS,ALL+1})
            end           
       after 1000 ->
          %%%io:format("Try Again ~p~n", [self()]),
          node_tell(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL})
    end.

%%%http://www.erlang.org/cgi-bin/ezmlm-cgi/3/457
set_random_seed(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) ->
    {_, _, Micros} = now(),
    A = erlang:phash2([make_ref(), self(), Micros]),
    random:seed(A, A, A),
    node_tell(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}).
    
start(5,ALL) ->
    register(node5, spawn(prjT, set_random_seed, [5,"KnowAndTell",ALL,[],{0,0,0,0}])),
    register(node4, spawn(prjT, set_random_seed, [4,"KnowAndTell",ALL,[],{0,0,0,0}])),
    register(node3, spawn(prjT, set_random_seed, [3,"KnowAndTell",ALL,[],{0,0,0,0}])),
    register(node2, spawn(prjT, set_random_seed, [2,"KnowAndTell",ALL,[],{0,0,0,0}])),
    register(node1, spawn(prjT, set_random_seed, [1,"KnowAndTell",ALL,[],{0,0,0,0}]));
start(N,ALL) -> 
    %%%if 
    %%%  N > 200 ->  
    register(list_to_atom("node" ++ integer_to_list(N)), spawn(prjT, set_random_seed, [N,"DontTell",ALL,[],{0,0,0,0}])),
    %%%  true ->  
    %%%    register(list_to_atom("node" ++ integer_to_list(N)), spawn(prjT, set_random_seed, [N,"KnowAndTell",ALL,[],{0,0,0,0}]))
    %%%end,
    start(N-1,ALL).


close(0) ->
  io:format("Done~n", []);
close(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! close,
  close(N-1).
  
status(0,{T,K,D,ID,WD,A}) ->
  receive
    {MYNUM,STATUS,WIN,DRAW,LOSS,ALL} ->
      if
        STATUS == "KnowAndTell" ->
          {NEWT,NEWK,NEWD} = {T+1,K,D};
        STATUS == "KnowDontTell" ->  
          {NEWT,NEWK,NEWD} = {T,K+1,D};
        STATUS == "DontTell" ->
          {NEWT,NEWK,NEWD} = {T,K,D+1};
        true->
          {NEWT,NEWK,NEWD}  = {T,K,D},
          io:format("????? Status:~p ~n", [STATUS])
      end,
      
      if 
        WIN + DRAW > WD ->
          status(0,{NEWT,NEWK,NEWD,MYNUM,WIN+DRAW,ALL});
        true ->
          status(0,{NEWT,NEWK,NEWD,ID,WD,A})
      end
    after 1000 ->
      io:format("Done Status~nTell:~p~nKnow:~p~nDont:~p~nID:~p ~p/~p~n", [T,K,D,ID,WD,A])
  end;
status(N,_) ->
  list_to_atom("node" ++ integer_to_list(N)) ! {status,self()},
  status(N-1,{0,0,0,0,0,0}).
  
  
  
stats(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! stats.
  
print([A,B,C,D,E,F,G,H,I]) ->
  io:format("~n ~p | ~p | ~p ~n", [A,B,C]),
  io:format("-----------~n", []),
  io:format(" ~p | ~p | ~p ~n", [D,E,F]),
  io:format("-----------~n", []),
  io:format(" ~p | ~p | ~p ~n~n", [G,H,I]).

  
mergeMoves([],NEWMOVES)->
  NEWMOVES;
mergeMoves([{MOVEBOARD,MOVE}|REST],NEWMOVES)->
  RAND = random:uniform(),
  if 
    RAND < 0.10 ->
      %%%doesn't matter what player I send, not using the new board
      {_,NEWMOVE} = move(MOVEBOARD,x,[]),
      mergeMoves(REST,NEWMOVES ++ [{MOVEBOARD,NEWMOVE}]);
    true->
      mergeMoves(REST,NEWMOVES ++ [{MOVEBOARD,MOVE}])
  end.
  
  
  
    
t(MOVES1,MOVES2)->
  if
    length(MOVES1) < 3 ->
      MOVES2;
    length(MOVES2) < 3 ->
      MOVES1;
    true ->
      R1 = random:uniform(length(MOVES1)-2)+1,
      {MOVES1H,MOVES1T} = lists:split(R1,MOVES1),
      R2 = random:uniform(length(MOVES2)-2)+1,
      {MOVES2H,MOVES2T} = lists:split(R2,MOVES2),
      
      R3 = random:uniform(),
      if 
        R3 > 0.5 ->
          NEWMOVES = MOVES1H ++ MOVES2T;
        true ->
          NEWMOVES = MOVES2H ++ MOVES1T
      end,
      
      %%%R4 = random:uniform(),
      if 
        length(NEWMOVES) < 5000 ->
          NEWMOVES;
        true ->
          mutate(NEWMOVES,[])
      end
  end.
  
mutate([],MERGEMOVES)->
  MERGEMOVES;
mutate([{MOVEBOARD,MOVE}|REST],MERGEMOVES)->
  RAND = random:uniform(),
  if 
    RAND < 0.10 ->
      %%%doesn't matter what player I send, not using the new board
      {_,NEWMOVE} = move(MOVEBOARD,x,[]),
      CKMERGE = checkExists(MOVEBOARD,MERGEMOVES);
    true ->
      NEWMOVE =  MOVE,
      CKMERGE = checkExists(MOVEBOARD,MERGEMOVES)
  end,

  if not CKMERGE ->
    mergeMoves(REST,MERGEMOVES ++ [{MOVEBOARD,NEWMOVE}]);
  true ->
    mergeMoves(REST,MERGEMOVES)
  end.
  
checkExists(_,[]) ->
  false;
checkExists([P0,P1,P2,P3,P4,P5,P6,P7,P8],[{MOVEBOARD,_}|REST]) ->
  if 
    [P0,P1,P2,P3,P4,P5,P6,P7,P8] == MOVEBOARD->
      true;
    [P6,P3,P0,P7,P4,P1,P8,P5,P2] == MOVEBOARD->
      true;
    [P8,P7,P6,P5,P4,P3,P2,P1,P0] == MOVEBOARD->
      true;
    [P2,P5,P8,P1,P4,P7,P0,P3,P6] == MOVEBOARD->
      true;
    true ->
     checkExists([P0,P1,P2,P3,P4,P5,P6,P7,P8],REST)
  end.


%%%move
%%%checks the moves and moves there if one matches
%%%if no positions match finds a space and makes a random move
move(BOARD,PLAYER,[]) ->
  %%%random:seed(now()),
  RAND = random:uniform(9),
  CURR = lists:nth(RAND,BOARD),
  if CURR == s ->
    {BOARDHEAD,BOARDTAIL} = lists:split(RAND-1,BOARD),
     %%%New board = old board with plays move inserted
     %%%No new stragegy added
    {BOARDHEAD ++ [PLAYER] ++ lists:nthtail(1,BOARDTAIL), RAND-1};
  true ->
    move(BOARD,PLAYER,[])
  end;
%%%checks all rotations
%%%New board = old board with plays move inserted
%%%No new stragegy added
move([P0,P1,P2,P3,P4,P5,P6,P7,P8],PLAYER,[{MOVEBOARD,MOVE}| REST]) ->
  if 
    [P0,P1,P2,P3,P4,P5,P6,P7,P8] == MOVEBOARD->
      {BOARDHEAD,BOARDTAIL} = lists:split(MOVE,[P0,P1,P2,P3,P4,P5,P6,P7,P8] ),
      {BOARDHEAD ++ [PLAYER] ++ lists:nthtail(1,BOARDTAIL), -1};
    [P6,P3,P0,P7,P4,P1,P8,P5,P2] == MOVEBOARD->
      NEWMOVE = 
      if MOVE == 0 -> 6;
         MOVE == 1 -> 3;
         MOVE == 2 -> 0;
         MOVE == 3 -> 7;
         MOVE == 4 -> 4;
         MOVE == 5 -> 1;
         MOVE == 6 -> 8;
         MOVE == 7 -> 5;
         MOVE == 8 -> 2
      end,
      {BOARDHEAD,BOARDTAIL} = lists:split(NEWMOVE,[P0,P1,P2,P3,P4,P5,P6,P7,P8] ),
      {BOARDHEAD ++ [PLAYER] ++ lists:nthtail(1,BOARDTAIL), -1};
    [P8,P7,P6,P5,P4,P3,P2,P1,P0] == MOVEBOARD->
      {BOARDHEAD,BOARDTAIL} = lists:split(8-MOVE,[P0,P1,P2,P3,P4,P5,P6,P7,P8] ),
      {BOARDHEAD ++ [PLAYER] ++ lists:nthtail(1,BOARDTAIL), -1};
    [P2,P5,P8,P1,P4,P7,P0,P3,P6] == MOVEBOARD->
      NEWMOVE = 
      if MOVE == 0 -> 2;
         MOVE == 1 -> 5;
         MOVE == 2 -> 8;
         MOVE == 3 -> 1;
         MOVE == 4 -> 4;
         MOVE == 5 -> 7;
         MOVE == 6 -> 0;
         MOVE == 7 -> 3;
         MOVE == 8 -> 6
      end,
      {BOARDHEAD,BOARDTAIL} = lists:split(NEWMOVE,[P0,P1,P2,P3,P4,P5,P6,P7,P8] ),
      {BOARDHEAD ++ [PLAYER] ++ lists:nthtail(1,BOARDTAIL), -1};
    true ->
      move([P0,P1,P2,P3,P4,P5,P6,P7,P8] ,PLAYER,REST)
  end.

checkgame([P1,P2,P3,P4,P5,P6,P7,P8,P9]) ->
  %%%print([P1,P2,P3,P4,P5,P6,P7,P8,P9]),
  if
    ([P1,P2,P1 /= s] == [P2,P3,true])  ->
      P1;
    ([P4,P5,P4 /= s] == [P5,P6,true])  ->
      P4;  
    ([P7,P8,P7 /= s] == [P8,P9,true])  ->
      P7;
    ([P1,P4,P1 /= s] == [P4,P7,true])  ->
      P1;
    ([P2,P5,P2 /= s] == [P5,P8,true])  ->
      P2;
    ([P3,P6,P3 /= s] == [P6,P9,true])  ->
      P3;
    ([P1,P5,P1 /= s] == [P5,P9,true])  ->
      P1;
    ([P3,P5,P3 /= s] == [P5,P7,true])  ->
      P3;
     P1 == s ->
      n;
     P2 == s ->
      n;
     P3 == s ->
      n;
     P4 == s ->
      n;
     P5 == s ->
      n;
     P6 == s ->
      n;
     P7 == s ->
      n;
     P8 == s ->
      n;
     P9 == s ->
      n;
    true ->
      d
  end.

play(BOARD,TURN,MOVES1,MOVES2) ->
  WINNER = checkgame(BOARD),
  if
    WINNER /= n ->
      {WINNER,MOVES1,MOVES2};
    TURN == x ->
      {NEWBOARD,NEWPOS} = move(BOARD,x,MOVES1),
      if NEWPOS == -1 ->
        play(NEWBOARD,o,MOVES1,MOVES2);
      true ->
        play(NEWBOARD,o,MOVES1 ++ [{BOARD,NEWPOS}],MOVES2)
      end;
    TURN == o ->
      {NEWBOARD,NEWPOS} = move(BOARD,o,MOVES2),
      if NEWPOS == -1 ->
        play(NEWBOARD,x,MOVES1,MOVES2);
      true ->
        play(NEWBOARD,x,MOVES1,MOVES2 ++ [{BOARD,NEWPOS}])
      end
  end.
