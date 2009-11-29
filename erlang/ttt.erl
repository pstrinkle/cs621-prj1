-module(ttt).

-export([node_tell/5,node_rec/5,start/2,close/1,status/2,stats/1,print/1,move/3,checkgame/1,play/4,set_random_seed/5,replaceM/2,mergeMoves/3,boardMatch/2,checkAll/2]).


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
            node_tell(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
        stats ->
            %%%io:format("~n~p~n~p~n~p~n~p~n~p", [MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}]),
            
            {ok, WriteDescr} = file:open(test.erl, [append]),
            io:fwrite(WriteDescr, "~n~p).~n%%%~p~n~p~n~p~n~p", [MYMOVES,MYNUM,STATUS,NUMNODES,{WIN,DRAW,LOSS,ALL}]),
            file:close(WriteDescr),

            node_tell(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
        {{NEWWIN,NEWDRAW,NEWLOSS,NEWALL},MYNEWMOVES} ->
          if 
            NEWLOSS > 0 ->
              node_tell(MYNUM,STATUS,NUMNODES,MYNEWMOVES,{0,0,0,NEWALL});
            NEWWIN + NEWDRAW > 1000 ->
              io:format("DRAWS! ~p | ~p | ~p~n", [MYNUM,STATUS,{NEWWIN,NEWDRAW,NEWLOSS,NEWALL}]),
              node_rec(MYNUM,"KnowDontTell",NUMNODES,MYNEWMOVES,{NEWWIN,NEWDRAW,NEWLOSS,NEWALL});
            true ->
              node_tell(MYNUM,STATUS,NUMNODES,MYNEWMOVES,{NEWWIN,NEWDRAW,NEWLOSS,NEWALL})
          end;
        {NODE_ID,THEIRMOVES,{THEIRWIN,THEIRDRAW,THEIRLOSS,THEIRALL}} ->
            {WINNER,THEIRNEWMOVES,MYNEWMOVES} = play([s,s,s,s,s,s,s,s,s],x,THEIRMOVES,MYMOVES),
            if 
              WINNER == x ->
                NODE_ID ! {{THEIRWIN+1,THEIRDRAW,THEIRLOSS,THEIRALL+1},THEIRNEWMOVES},
                node_rec(MYNUM,STATUS,NUMNODES,mergeMoves(THEIRNEWMOVES,MYNEWMOVES,[]),{WIN,DRAW,LOSS+1,ALL+1});
              WINNER == o ->
                NODE_ID ! {{0,0,0,THEIRALL+1},mergeMoves(MYNEWMOVES,THEIRNEWMOVES,[])},
                %%%if 
                %%%  WIN > 0 ->
                node_rec(MYNUM,STATUS,NUMNODES,MYNEWMOVES,{WIN+1,DRAW,LOSS,ALL+1});
                %%%  true ->
                %%%   node_rec(MYNUM,STATUS,NUMNODES,MYNEWMOVES,{WIN+1,DRAW,LOSS,ALL+1})
                %%% end;
              true ->
                NODE_ID !  {{THEIRWIN,THEIRDRAW+1,THEIRLOSS,THEIRALL+1},THEIRNEWMOVES},
                node_rec(MYNUM,STATUS,NUMNODES,MYNEWMOVES,{WIN,DRAW+1,LOSS,ALL+1})
            end           
       %%%after 1000 ->
          %%%io:format("Try Again ~p~n", [self()]),
         %%% node_tell(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL})
    end.

%%%http://www.erlang.org/cgi-bin/ezmlm-cgi/3/457
set_random_seed(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) ->
    {_, _, Micros} = now(),
    A = erlang:phash2([make_ref(), self(), Micros]),
    random:seed(A, A, A),
    node_tell(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}).
    
start(5,ALL) ->
    register(node5, spawn(ttt, set_random_seed, [5,"KnowAndTell",ALL,[],{0,0,0,0}])),
    register(node4, spawn(ttt, set_random_seed, [4,"KnowAndTell",ALL,[],{0,0,0,0}])),
    register(node3, spawn(ttt, set_random_seed, [3,"KnowAndTell",ALL,[],{0,0,0,0}])),
    register(node2, spawn(ttt, set_random_seed, [2,"KnowAndTell",ALL,[],{0,0,0,0}])),
    register(node1, spawn(ttt, set_random_seed, [1,"KnowAndTell",ALL,[],{0,0,0,0}]));
start(N,ALL) -> 
    if 
      N > 100 ->  
        register(list_to_atom("node" ++ integer_to_list(N)), spawn(ttt, set_random_seed, [N,"DontTell",ALL,[],{0,0,0,0}]));
      true ->  
        register(list_to_atom("node" ++ integer_to_list(N)), spawn(ttt, set_random_seed, [N,"KnowAndTell",ALL,[],{0,0,0,0}]))
    end,
    start(N-1,ALL).


close(0) ->
  io:format("Done~n", []);
close(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! close,
  close(N-1).
  
status(0,{T,K,D,ID,WD,A}) ->
  receive
    {MYNUM,STATUS,WIN,DRAW,_,ALL} ->
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
    {BOARDHEAD ++ [PLAYER] ++ lists:nthtail(1,BOARDTAIL),
     BOARDHEAD ++ [m] ++ lists:nthtail(1,BOARDTAIL)};
  true ->
    move(BOARD,PLAYER,[])
  end;
%%%checks all rotations
%%%New board = old board with plays move inserted
%%%No new stragegy added
move(BOARD,PLAYER,[MOVEBOARD|REST]) ->
  MATCHBOARD = boardMatch(BOARD,MOVEBOARD),
  if
    MATCHBOARD /= [] ->
      {replaceM(MATCHBOARD,PLAYER),[]};
    true ->
      move(BOARD,PLAYER,REST)
  end.

checkAll([],LOSEMOVE) ->
  false;
checkAll([WINHEAD|WINREST],LOSEMOVE) ->
  CK = boardMatch(replaceM(WINHEAD,s),LOSEMOVE),
  if 
    CK /= [] ->
      true;
    true ->
      checkAll(WINREST,LOSEMOVE)
  end.

mergeMoves(WINMOVES,[],ADDMOVES) ->
  %%%io:format("~p - ~p~n",[length(WINMOVES),length(ADDMOVES)]),
  WINMOVES ++ ADDMOVES;
mergeMoves(WINMOVES,[LOSEHEAD|LOSEREST],ADDMOVES) ->
  CK = checkAll(WINMOVES,LOSEHEAD),
  if 
    CK ->
      mergeMoves(WINMOVES,LOSEREST,ADDMOVES);
    true ->
      %%%should pick one or the other && mutate
      RAND = random:uniform(),
      if 
        RAND < 0.10 ->
          %%%doesn't matter what player I send, not using the new board
          MOVEBOARD = replaceM(LOSEHEAD,s),
          {_,NEWMOVE} = move(MOVEBOARD,x,[]),
          mergeMoves(WINMOVES,LOSEREST,ADDMOVES ++ [NEWMOVE]);
        true ->
          mergeMoves(WINMOVES,LOSEREST,ADDMOVES ++ [LOSEHEAD])
      end
  end.

replaceM([m,P1,P2,P3,P4,P5,P6,P7,P8],PLAYER) ->
  [PLAYER,P1,P2,P3,P4,P5,P6,P7,P8];
replaceM([P0,m,P2,P3,P4,P5,P6,P7,P8],PLAYER) ->
  [P0,PLAYER,P2,P3,P4,P5,P6,P7,P8];
replaceM([P0,P1,m,P3,P4,P5,P6,P7,P8],PLAYER) ->
  [P0,P1,PLAYER,P3,P4,P5,P6,P7,P8];
replaceM([P0,P1,P2,m,P4,P5,P6,P7,P8],PLAYER) ->
  [P0,P1,P2,PLAYER,P4,P5,P6,P7,P8];
replaceM([P0,P1,P2,P3,m,P5,P6,P7,P8],PLAYER) ->
  [P0,P1,P2,P3,PLAYER,P5,P6,P7,P8];
replaceM([P0,P1,P2,P3,P4,m,P6,P7,P8],PLAYER) ->
  [P0,P1,P2,P3,P4,PLAYER,P6,P7,P8];
replaceM([P0,P1,P2,P3,P4,P5,m,P7,P8],PLAYER) ->
  [P0,P1,P2,P3,P4,P5,PLAYER,P7,P8];
replaceM([P0,P1,P2,P3,P4,P5,P6,m,P8],PLAYER) ->
  [P0,P1,P2,P3,P4,P5,P6,PLAYER,P8];
replaceM([P0,P1,P2,P3,P4,P5,P6,P7,m],PLAYER) ->
  [P0,P1,P2,P3,P4,P5,P6,P7,PLAYER].
  
    
boardMatch(BOARD,[P0,P1,P2,P3,P4,P5,P6,P7,P8]) ->
  [R0,R1,R2,R3,R4,R5,R6,R7,R8] = replaceM([P0,P1,P2,P3,P4,P5,P6,P7,P8],s),
  if
    BOARD == [R0,R1,R2,R3,R4,R5,R6,R7,R8] ->
      [P0,P1,P2,P3,P4,P5,P6,P7,P8];
    BOARD == [R6,R3,R0,R7,R4,R1,R8,R5,R2] ->
      [P6,P3,P0,P7,P4,P1,P8,P5,P2];
    BOARD == [R8,R7,R6,R5,R4,R3,R2,R1,R0] ->
      [P8,P7,P6,P5,P4,P3,P2,P1,P0];
    BOARD == [R2,R5,R8,R1,R4,R7,R0,R3,R6] ->
      [P2,P5,P8,P1,P4,P7,P0,P3,P6];
    BOARD == [R6,R7,R8,R3,R4,R5,R0,R1,R2] ->
      [P6,P7,P8,P3,P4,P5,P0,P1,P2];
    BOARD == [R0,R3,R6,R1,R4,R7,R2,R5,R8] ->
      [P0,P3,P6,P1,P4,P7,P2,P5,P8];   
    BOARD == [R2,R1,R0,R5,R4,R3,R8,R7,R6] ->
      [P2,P1,P0,P5,P4,P3,P8,P7,P6];
    BOARD == [R8,R5,R2,R7,R4,R1,R6,R3,R0] ->
      [P8,P5,P2,P7,P4,P1,P6,P3,P0];
    true ->
      []
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
      {NEWBOARD,NEWMOVEBOARD} = move(BOARD,x,MOVES1),
      if NEWMOVEBOARD == [] ->
        play(NEWBOARD,o,MOVES1,MOVES2);
      true ->
        play(NEWBOARD,o,MOVES1 ++ [NEWMOVEBOARD],MOVES2)
      end;
    TURN == o ->
      {NEWBOARD,NEWMOVEBOARD} = move(BOARD,o,MOVES2),
      if NEWMOVEBOARD == [] ->
        play(NEWBOARD,x,MOVES1,MOVES2);
      true ->
        play(NEWBOARD,x,MOVES1,MOVES2 ++ [NEWMOVEBOARD])
      end
  end.
