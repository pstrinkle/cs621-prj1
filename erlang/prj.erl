-module(prj).

-export([node_tell/3,node_rec/3,start/2,close/1,status/1]).

getRand(MYNUM,NUMNODES) ->
  RANDNUM = random:uniform(NUMNODES),
  if
    RANDNUM == MYNUM ->
      getRand(MYNUM,NUMNODES);
    true ->
      "node" ++ integer_to_list(RANDNUM)
  end.

node_tell(MYNUM,STATUS,NUMNODES) ->
    if
      STATUS == "KnowAndTell" ->
          %%%if know pick random node and tell it the msg
          MSGNODE = getRand(MYNUM,NUMNODES),
          io:format("~p Telling ~p~n", [self(),MSGNODE]),
          list_to_atom(MSGNODE) ! self(),
          node_rec(MYNUM,STATUS,NUMNODES) ;
      true ->
          node_rec(MYNUM,STATUS,NUMNODES)
    end.

node_rec(MYNUM,STATUS,NUMNODES) ->
    receive
        close ->
           io:format("Stoping ~p~n", [self()]);
        status ->
           io:format("Status ~p:~p~n", [self(),STATUS]),
           node_rec(MYNUM,STATUS,NUMNODES);
        knew ->
          RANDNUM = random:uniform(),
          io:format("Knew ~p ~p~n", [RANDNUM,self()]),
          if
            RANDNUM < 0.05 ->
              node_rec(MYNUM,"KnowDontTell",NUMNODES);
            true ->
              node_rec(MYNUM,STATUS,NUMNODES)
          end;
        learned ->
            node_rec(MYNUM,STATUS,NUMNODES);
        NODE_ID ->
            if
              STATUS == "DontKnow" ->
                io:format("~p Learned From ~p~n", [self(),NODE_ID]),
                NODE_ID ! learned,
                node_rec(MYNUM,"KnowAndTell",NUMNODES);
              true ->
                NODE_ID ! knew,
                node_rec(MYNUM,STATUS,NUMNODES)
            end
       after 100 ->
          %%%io:format("Try Again ~p~n", [self()]),
          node_tell(MYNUM,STATUS,NUMNODES)
    end.

start(1,TOTAL) ->
    register(node1, spawn(prj, node_tell, [1,"KnowAndTell",TOTAL]));
start(N,TOTAL) ->
    register(list_to_atom("node" ++ integer_to_list(N)), spawn(prj, node_tell, [N,"DontKnow",TOTAL])),
    start(N-1,TOTAL).

close(0) ->
  io:format("Done~n", []);
close(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! close,
  close(N-1).

status(0) ->
  io:format("Done Status~n", []);
status(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! status,
  status(N-1).
