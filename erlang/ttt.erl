-module(ttt).

%%%ttt:start(NUMNODES,NUMNODES). to start with NUMNODES process
%%%ttt:status(NUMNODES,_). to print the current status ( _ can be anything)
%%%ttt:close(NUMNODES) to close all running process
%%% when a process win/draws 1000 games without losing it writes its moves to
%%% test.erl and closes all process

-export([node_play/5,node_rec_game/5,start/2,close/1,status/2,stats/1,print/1,move/3,checkgame/1,play/6,set_random_seed/5,mergeMoves/3,eraseAll/2,mergeAll/2,getRand/2]).

%%%selects a rand node between 1 and NUMMODES other than MYNUM
getRand(MYNUM,NUMNODES) ->
  RANDNUM = random:uniform(NUMNODES),
  if
    RANDNUM == MYNUM ->
      getRand(MYNUM,NUMNODES);
    true ->
      list_to_atom("node" ++ integer_to_list(RANDNUM))
  end.

%%%if in stats knowAndTell ask a node to play then wait for response
%%%otherwise just wait for a response
node_play(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) ->
    if 
      STATUS == knowAndTell ->
          %%%if know pick random node and tell it the msg
          MSGNODE = getRand(MYNUM,NUMNODES),
          %%%sends message with id, moves, record
          MSGNODE ! {MYNUM,MYMOVES,{WIN,DRAW,LOSS,ALL}},
          %%%log(MYNUM,MSGNODE,"send game"),
          node_rec_game(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
      true ->
          node_rec_game(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) 
    end.

  
%%%waits for a response
%%%close: stops process
%%%{status,NODE_ID}: sends status to NODE_ID
%%%stats: writes stats to a file
%%%{{NEWWIN,NEWDRAW,NEWLOSS,NEWALL},MYNEWMOVES}: logs response from a game, then calls node_play
%%%{NODE_ID,THEIRMOVES,{THEIRWIN,THEIRDRAW,THEIRLOSS,THEIRALL}}: plays a game with NODE_ID and then sends the results back

node_rec_game(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) ->          
     receive
        close ->
            io:format("Stoping ~p~n", [self()]);  
        {status,NODE_ID} ->
            NODE_ID ! {MYNUM,STATUS,WIN,DRAW,LOSS,ALL,length(dict:to_list(MYMOVES)),NUMNODES},
            node_rec_game(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
        stats ->            
            {ok, WriteDescr} = file:open(test.erl, [append]),
            io:fwrite(WriteDescr, "~n~p).~n%%%~p ~p ~p ~p", [MYMOVES,MYNUM,STATUS,NUMNODES,{WIN,DRAW,LOSS,ALL}]),
            file:close(WriteDescr),
            node_rec_game(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
        {{NEWWIN,NEWDRAW,NEWLOSS,NEWALL},MYNEWMOVES,THEIRNUM} ->
            if
              NEWWIN + NEWDRAW > 3000 ->         
                log(MYNUM,THEIRNUM,"3000"),
                node_rec_game(MYNUM,knowDontTell,NUMNODES,MYNEWMOVES,{NEWWIN,NEWDRAW,NEWLOSS,NEWALL});
              true ->
                node_play(MYNUM,knowAndTell,NUMNODES,MYNEWMOVES,{NEWWIN,NEWDRAW,NEWLOSS,NEWALL})
            end;
        {NODE_ID,THEIRMOVES,{THEIRWIN,THEIRDRAW,THEIRLOSS,THEIRALL}} ->
            %%%log(MYNUM,NODE_ID,"receive game"),
            %%%know perfect strag, no need to play another game, just tell person so they know too
            if 
              STATUS == knowDontTell ->
                log(MYNUM,NODE_ID,"told 3000"),
                NODE_ID ! {{WIN,DRAW,LOSS,ALL},MYMOVES,MYNUM},
                node_rec_game(MYNUM,knowDontTell,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL});
              STATUS == dontTell ->
                {WINNER,MYNEWMOVES,THEIRNEWMOVES} = play([s,s,s,s,s,s,s,s,s],x,MYMOVES,[],THEIRMOVES,[]),
                if 
                  WINNER == x ->
                    NODE_ID ! {{0,0,0,THEIRALL+1},mergeMoves(THEIRMOVES,MYNEWMOVES,THEIRNEWMOVES),MYNUM},
                    node_play(MYNUM,knowAndTell,NUMNODES,mergeMoves(MYMOVES,MYNEWMOVES,THEIRNEWMOVES),{WIN+1,DRAW,LOSS,ALL+1});
                  WINNER == o ->
                    NODE_ID ! {{THEIRWIN+1,THEIRDRAW,THEIRLOSS,THEIRALL+1},mergeMoves(THEIRMOVES,THEIRNEWMOVES,MYNEWMOVES),MYNUM},
                    node_play(MYNUM,knowAndTell,NUMNODES,mergeMoves(MYMOVES,THEIRNEWMOVES,MYNEWMOVES),{0,0,0,ALL+1});
                  true ->
                    NODE_ID !  {{THEIRWIN,THEIRDRAW+1,THEIRLOSS,THEIRALL+1},mergeMoves(THEIRMOVES,THEIRNEWMOVES,[]),MYNUM},
                    node_play(MYNUM,knowAndTell,NUMNODES,mergeMoves(MYMOVES,THEIRNEWMOVES,[]),{WIN,DRAW+1,LOSS,ALL+1})
                end;
              true ->
                {WINNER,MYNEWMOVES,THEIRNEWMOVES} = play([s,s,s,s,s,s,s,s,s],x,MYMOVES,[],THEIRMOVES,[]),
                if 
                  WINNER == x ->
                    NODE_ID ! {{0,0,0,THEIRALL+1},mergeMoves(THEIRMOVES,MYNEWMOVES,THEIRNEWMOVES),MYNUM},
                    node_rec_game(MYNUM,knowAndTell,NUMNODES,mergeMoves(MYMOVES,MYNEWMOVES,THEIRNEWMOVES),{WIN+1,DRAW,LOSS,ALL+1});
                  WINNER == o ->
                    NODE_ID ! {{THEIRWIN+1,THEIRDRAW,THEIRLOSS,THEIRALL+1},mergeMoves(THEIRMOVES,THEIRNEWMOVES,MYNEWMOVES),MYNUM},
                    node_rec_game(MYNUM,knowAndTell,NUMNODES,mergeMoves(MYMOVES,THEIRNEWMOVES,MYNEWMOVES),{0,0,0,ALL+1});
                  true ->
                    NODE_ID !  {{THEIRWIN,THEIRDRAW+1,THEIRLOSS,THEIRALL+1},mergeMoves(THEIRMOVES,THEIRNEWMOVES,[]),MYNUM},
                    node_rec_game(MYNUM,knowAndTell,NUMNODES,mergeMoves(MYMOVES,THEIRNEWMOVES,[]),{WIN,DRAW+1,LOSS,ALL+1})
                end
            end
     end.

log(NODE1,NODE2,MSG) ->
  {ok, WriteDescr} = file:open(log.txt, [append]),
  io:fwrite(WriteDescr, "~p\t~p\t~p~n", [NODE1,NODE2,MSG]),
  file:close(WriteDescr).


%%%sets a random seed
%%%code from: http://www.erlang.org/cgi-bin/ezmlm-cgi/3/457
set_random_seed(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL}) ->
    {_, _, Micros} = now(),
    A = erlang:phash2([make_ref(), self(), Micros]),
    random:seed(A, A, A),
    
    receive
      a ->
        io:format("as",[])
      after 1000 ->
        node_play(MYNUM,STATUS,NUMNODES,MYMOVES,{WIN,DRAW,LOSS,ALL})
    end.
    
%%%starts 5 nodes in status knowAndTell
%%%starting a few gets the message out faster
start(1,ALL) ->
    register(node1, spawn(ttt, set_random_seed, [node1,knowAndTell,ALL,dict:new(),{0,0,0,0}]));
start(N,ALL) ->
    register(list_to_atom("node" ++ integer_to_list(N)), spawn(ttt, set_random_seed, [list_to_atom("node" ++ integer_to_list(N)),dontTell,ALL,dict:new(),{0,0,0,0}])),
    start(N-1,ALL).

%%%send a message to N nodes to close
close(0) ->
  io:format("Done~n", []);
close(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! close,
  close(N-1).
  
%%%gathers the status of N nodes and prints it
status(0,{T,K,D,ID,WD,A,L,N}) ->
  receive
    {MYNUM,STATUS,WIN,DRAW,_,ALL,LEN,NUM} ->
      if
        STATUS == knowAndTell ->
          {NEWT,NEWK,NEWD} = {T+1,K,D};
        STATUS == knowDontTell ->  
          {NEWT,NEWK,NEWD} = {T,K+1,D};
        STATUS == dontTell ->
          {NEWT,NEWK,NEWD} = {T,K,D+1};
        true->
          {NEWT,NEWK,NEWD}  = {T,K,D},
          io:format("????? Status:~p ~n", [STATUS])
      end,
      
      if 
        WIN + DRAW > WD ->
          status(0,{NEWT,NEWK,NEWD,MYNUM,WIN+DRAW,ALL,L+LEN,NUM});
        true ->
          status(0,{NEWT,NEWK,NEWD,ID,WD,A,L+LEN,NUM})
      end
    after 1000 ->
      io:format("Done Status~nTell:~p~nKnow:~p~nDont:~p~nID:~p ~p/~p~nAvg Len:~p~n", [T,K,D,ID,WD,A,L/N])
  end;
status(N,_) ->
  list_to_atom("node" ++ integer_to_list(N)) ! {status,self()},
  status(N-1,{0,0,0,0,0,0,0,0}).
  
%%%send a message to node N to print its stats
stats(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! stats.
  
%%%prints a board
print([A,B,C,D,E,F,G,H,I]) ->
  io:format("~n ~p | ~p | ~p ~n", [A,B,C]),
  io:format("-----------~n", []),
  io:format(" ~p | ~p | ~p ~n", [D,E,F]),
  io:format("-----------~n", []),
  io:format(" ~p | ~p | ~p ~n~n", [G,H,I]).
  
%%%removes REMOVE moves from MOVES and adds KEEP moves to MOVES
mergeMoves(MOVES,KEEP,REMOVE) ->
  mergeAll(eraseAll(MOVES,REMOVE),KEEP).
  
%%%removes all rotations and reflections of the move
eraseAll(MOVES,[]) ->
  MOVES;
eraseAll(MOVES,[{REMOVEKEY,_}|REST]) ->
  eraseAll(dict:erase(REMOVEKEY,dict:erase(rotate1(REMOVEKEY),dict:erase(rotate2(REMOVEKEY),dict:erase(rotate3(REMOVEKEY),dict:erase(reflect(REMOVEKEY),dict:erase(reflect1(REMOVEKEY),dict:erase(reflect2(REMOVEKEY),dict:erase(reflect3(REMOVEKEY),MOVES)))))))),REST).

%%%merges all moves into MOVES
%%%can't use the built in dict:merge because need to check for all rotations/reflections
mergeAll(MOVES,[]) ->
  MOVES;
mergeAll(MOVES,[{BOARD,MOVE}|REST]) ->
  ROTATE0 = dict:is_key({BOARD,MOVE},MOVES),
  ROTATE1 = dict:is_key(rotate1(BOARD),MOVES),
  ROTATE2 = dict:is_key(rotate2(BOARD),MOVES),
  ROTATE3 = dict:is_key(rotate3(BOARD),MOVES),
  REFLECT0 = dict:is_key(reflect(BOARD),MOVES),
  REFLECT1 = dict:is_key(reflect1(BOARD),MOVES),
  REFLECT2 = dict:is_key(reflect2(BOARD),MOVES),
  REFLECT3 = dict:is_key(reflect3(BOARD),MOVES),
  if 
    ROTATE0 ->
      mergeAll(MOVES,REST);
    ROTATE1 ->
      mergeAll(MOVES,REST);
    ROTATE2 ->
      mergeAll(MOVES,REST);
    ROTATE3 ->
      mergeAll(MOVES,REST);
    REFLECT0 ->
      mergeAll(MOVES,REST);
    REFLECT1 ->
      mergeAll(MOVES,REST);
    REFLECT2 ->
      mergeAll(MOVES,REST);
    REFLECT3 ->
      mergeAll(MOVES,REST);
    true ->
      mergeAll(dict:store(BOARD,MOVE,MOVES),REST)
  end.


%%%move
%%%checks the moves and moves there if one matches
%%%if no positions match finds a space and makes a random move
move(BOARD,PLAYER,MOVES) ->
  ROTATE0 = dict:is_key(BOARD,MOVES),
  ROTATE1 = dict:is_key(rotate1(BOARD),MOVES),
  ROTATE2 = dict:is_key(rotate2(BOARD),MOVES),
  ROTATE3 = dict:is_key(rotate3(BOARD),MOVES),
  REFLECT0 = dict:is_key(reflect(BOARD),MOVES),
  REFLECT1 = dict:is_key(reflect1(BOARD),MOVES),
  REFLECT2 = dict:is_key(reflect2(BOARD),MOVES),
  REFLECT3 = dict:is_key(reflect3(BOARD),MOVES),
  if 
    ROTATE0 ->
      dict:fetch(BOARD,MOVES);
    ROTATE1 ->
      rotate3(dict:fetch(rotate1(BOARD),MOVES));
    ROTATE2 ->
      rotate2(dict:fetch(rotate2(BOARD),MOVES));
    ROTATE3 ->
      rotate1(dict:fetch(rotate3(BOARD),MOVES));
    REFLECT0 ->
      reflect(dict:fetch(reflect(BOARD),MOVES));
    REFLECT1 ->
      reflect3(dict:fetch(reflect1(BOARD),MOVES));
    REFLECT2 ->
      reflect2(dict:fetch(reflect2(BOARD),MOVES));
    REFLECT3 ->
      reflect1(dict:fetch(reflect3(BOARD),MOVES));
    true ->
      makeRandMove(BOARD,PLAYER)
  end.

%%%rotates and reflects a board
rotate1([P0,P1,P2,P3,P4,P5,P6,P7,P8]) ->
    [P6,P3,P0,P7,P4,P1,P8,P5,P2].
rotate2([P0,P1,P2,P3,P4,P5,P6,P7,P8]) ->
    [P8,P7,P6,P5,P4,P3,P2,P1,P0]. 
rotate3([P0,P1,P2,P3,P4,P5,P6,P7,P8]) ->
    [P2,P5,P8,P1,P4,P7,P0,P3,P6]. 
reflect([P0,P1,P2,P3,P4,P5,P6,P7,P8]) ->
    [P6,P7,P8,P3,P4,P5,P0,P1,P2].    
reflect1([P0,P1,P2,P3,P4,P5,P6,P7,P8]) ->
    [P0,P3,P6,P1,P4,P7,P2,P5,P8].      
reflect2([P0,P1,P2,P3,P4,P5,P6,P7,P8]) ->
    [P2,P1,P0,P5,P4,P3,P8,P7,P6].   
reflect3([P0,P1,P2,P3,P4,P5,P6,P7,P8]) ->
    [P8,P5,P2,P7,P4,P1,P6,P3,P0]. 
    
%%%makes a random moves on a board
makeRandMove(BOARD,PLAYER) ->
  RAND = random:uniform(9),
  CURR = lists:nth(RAND,BOARD),
  if 
    CURR == s ->
      {BOARDHEAD,BOARDTAIL} = lists:split(RAND-1,BOARD),
      BOARDHEAD ++ [PLAYER] ++ lists:nthtail(1,BOARDTAIL);
    true ->
      makeRandMove(BOARD,PLAYER)
  end.
      
 
%%%checks for a winner
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

%%%plays a game of ttt and returns the winner and the new moves
play(BOARD,TURN,MOVES1,NEWMOVES1,MOVES2,NEWMOVES2) ->
  WINNER = checkgame(BOARD),
  if
    WINNER /= n ->
      {WINNER,NEWMOVES1,NEWMOVES2};
    TURN == x ->
      NEWBOARD = move(BOARD,x,MOVES1),
      play(NEWBOARD,o,MOVES1,NEWMOVES1 ++ [{BOARD,NEWBOARD}],MOVES2,NEWMOVES2);
    TURN == o ->
      NEWBOARD = move(BOARD,o,MOVES2),
      play(NEWBOARD,x,MOVES1,NEWMOVES1,MOVES2,NEWMOVES2 ++ [{BOARD,NEWBOARD}])
  end.
