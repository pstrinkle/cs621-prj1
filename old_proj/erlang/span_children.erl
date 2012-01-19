
%%% to compile: c(prj).
%%% to start: prj:start(N,N).
%%% to query: prj:status(N).
%%% to close: prj:close(N).
%%% to get a list of nodes: prj:identify().

-module(span_children).

-export([find_child/4,node_rec/5,start/2,close/1,status/1,identify/0]).

%%% Print Children List
printList([HEAD|[]]) ->
    io:format("~p~n", [HEAD]);
printList([HEAD|REST]) ->
    io:format("~p ", [HEAD]),
    printList(REST).

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
find_child(MYNUM, STATUS, NUMNODES, CHILDREN) ->
    if
      STATUS == "Member" ->          
          MSGNODE = getRand(MYNUM, NUMNODES),
          %io:format("~p Asks ~p~n", [self(), MSGNODE]),
          list_to_atom(MSGNODE) ! self(),
          node_rec(MYNUM, STATUS, NUMNODES, CHILDREN, MSGNODE);
      true ->
          node_rec(MYNUM, STATUS, NUMNODES, CHILDREN, "")
    end.

%%% Receive Messages
node_rec(MYNUM, STATUS, NUMNODES, CHILDREN, MSGNODE) ->
    receive
        close ->
           io:format("Stoping ~p~n", [self()]);
        status ->
           if
             length(CHILDREN) == 0 ->
               io:format("Status ~p:~p No Children~n", [self(), STATUS]);
             true ->
               io:format("Status ~p:~p Children:~p~n", [self(), STATUS, CHILDREN])
           end,
           node_rec(MYNUM, STATUS, NUMNODES, CHILDREN, MSGNODE);
        nojoy ->
          RANDNUM = random:uniform(),
          if
            RANDNUM < 0.05 ->
              io:format("I, (~p), quit.~n", [self()]),
              node_rec(MYNUM, "Quit", NUMNODES, CHILDREN, MSGNODE);
            true ->
              node_rec(MYNUM, STATUS, NUMNODES, CHILDREN, MSGNODE)
          end;
        child ->
            io:format("~p Attached a new child:~p~n", [self(), MSGNODE]),
            node_rec(MYNUM, STATUS, NUMNODES, CHILDREN++MSGNODE, MSGNODE);
        NODE_ID ->
            if
              STATUS == "Alone" ->
                io:format("~p now Child of ~p~n", [self(), NODE_ID]),
                NODE_ID ! child,
                node_rec(MYNUM, "Member", NUMNODES, CHILDREN, MSGNODE);
              true ->
                NODE_ID ! nojoy,
                node_rec(MYNUM, STATUS, NUMNODES, CHILDREN, MSGNODE)
            end
    %%% if no matching message has arrived within ExprT milliseconds
    after 100 ->
        if
          STATUS == "Member" ->
            find_child(MYNUM, STATUS, NUMNODES, CHILDREN);
          true ->
            node_rec(MYNUM, STATUS, NUMNODES, CHILDREN, MSGNODE)
        end
    end.

%%% Startup the System
start(1, TOTAL) ->
    register(node1, spawn(span_children, find_child, [1, "Member", TOTAL, []]));
start(N, TOTAL) ->
    PID = spawn(span_children, find_child, [N, "Alone", TOTAL, []]),
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
