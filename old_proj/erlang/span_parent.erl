
%%% to compile: c(prj).
%%% to start: prj:start(N,N).
%%% to query: prj:status(N).
%%% to close: prj:close(N).
%%% to get a list of nodes: prj:identify().

-module(span_parent).

-export([find_child/4,node_rec/4,start/2,close/1,status/1,identify/0]).

%%% Get Random Number
getRand(MYNUM, NUMNODES) ->
    random:seed(now()),
    RANDNUM = random:uniform(NUMNODES),
    if
      RANDNUM == MYNUM ->
        getRand(MYNUM, NUMNODES);
      true ->
        "node" ++ integer_to_list(RANDNUM)
    end.

%%% Find Nodes to be PARENT
find_child(MYNUM, STATUS, NUMNODES, PARENT) ->
    if
      STATUS == "Member" ->
          %%% if know pick random node and tell it the msg
          %%% downside is I currently don't track my PARENT
          %%% therefore i might message my child and then stop
          %%% trying to find dudes--maybe that's ok?
          MSGNODE = getRand(MYNUM, NUMNODES),
          %%%io:format("~p Asks ~p~n", [self(), MSGNODE]),
          list_to_atom(MSGNODE) ! self(),
          node_rec(MYNUM, STATUS, NUMNODES, PARENT);
      true ->
          node_rec(MYNUM, STATUS, NUMNODES, PARENT)
    end.

%%% Receive Messages
node_rec(MYNUM, STATUS, NUMNODES, PARENT) ->
    receive
        close ->
           io:format("Stoping ~p~n", [self()]);
        status ->
           io:format("Status ~p:~p Child Of: ~p~n", [self(), STATUS, PARENT]),
           node_rec(MYNUM, STATUS, NUMNODES, PARENT);
        nojoy ->
          RANDNUM = random:uniform(),
          %%%io:format("I, ~p, Attempted to attach ~p~n", [self(), RANDNUM]),
          if
            RANDNUM < 0.05 ->
              io:format("I, (~p), quit.~n", [self()]),
              node_rec(MYNUM, "Quit", NUMNODES, PARENT);
            true ->
              node_rec(MYNUM, STATUS, NUMNODES, PARENT)
          end;
        child ->
            %%%io:format("~p Attached a new child.~n", [self()]),
            node_rec(MYNUM, STATUS, NUMNODES, PARENT);
        NODE_ID ->
            if
              STATUS == "Alone" ->
                io:format("~p now Child of ~p~n", [self(), NODE_ID]),
                NODE_ID ! child,
                node_rec(MYNUM, "Member", NUMNODES, NODE_ID);
              true ->
                NODE_ID ! nojoy,
                node_rec(MYNUM, STATUS, NUMNODES, PARENT)
            end
    %%% if no matching message has arrived within ExprT milliseconds
    after 100 ->
        if
          STATUS == "Member" ->
            find_child(MYNUM, STATUS, NUMNODES, PARENT);
          true ->
            node_rec(MYNUM, STATUS, NUMNODES, PARENT)
        end
    end.

%%% Startup the System
start(1, TOTAL) ->
    register(node1, spawn(span_parent, find_child, [1, "Member", TOTAL, 0]));
start(N, TOTAL) ->
    PID = spawn(span_parent, find_child, [N, "Alone", TOTAL, 0]),
    io:format("~p is node~p~n", [PID, N]),
    register(list_to_atom("node" ++ integer_to_list(N)), PID),
    start(N-1, TOTAL).

%%% Shutdown the System
close(0) ->
  io:format("Done~n", []);
close(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! close,
  close(N-1).

%%% Status of the System
status(0) ->
  io:format("Done Status~n", []);
status(N) ->
  list_to_atom("node" ++ integer_to_list(N)) ! status,
  status(N-1).

%%% This lists all registered nodes by name
identify() ->
  io:format("nodes: ~p~n", [registered()]).
