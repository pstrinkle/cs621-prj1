
%%% to compile: c(prj).
%%% to start: prj:start(N,N).
%%% to query: prj:status(N).
%%% to close: prj:close(N).
%%% to get a list of nodes: prj:identify().

-module(prj_avg).

-export([node_tell/5,node_rec/5,start/2,close/1,status/1,identify/0]).

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

%%% Tell Other Nodes
node_tell(MYNUM, STATUS, NUMNODES, VALUE, TRIES) ->
    if
      TRIES == 2 * NUMNODES ->
        node_rec(MYNUM, "KnowDontTell", NUMNODES, VALUE, TRIES);
      true ->
        if
          STATUS == "KnowAndTell" ->
            MSGNODE = getRand(MYNUM, NUMNODES),
            io:format("~p Tells ~p~n", [self(), MSGNODE]),
            list_to_atom(MSGNODE) ! {self(), VALUE},
            node_rec(MYNUM, STATUS, NUMNODES, VALUE, TRIES);
          true ->
            node_rec(MYNUM, STATUS, NUMNODES, VALUE, TRIES)
        end
    end.

%%% Receive Messages
node_rec(MYNUM, STATUS, NUMNODES, VALUE, TRIES) ->
    receive
        close ->
           io:format("Stoping ~p~n", [self()]);
        status ->
           io:format("Status ~p:~p Value:~p~n", [self(), STATUS, VALUE]),
           node_rec(MYNUM, STATUS, NUMNODES, VALUE, TRIES);
        {NODE_ID, THEIR_VALUE} ->
            io:format("I, ~p(~p): received: ~p:~p~n", [self(), STATUS, NODE_ID, THEIR_VALUE]),
            if
              STATUS == "KnowAndTell" ->
                if
                  THEIR_VALUE == VALUE ->
                    io:format("Values Match! (~p, ~p)~n", [self(), NODE_ID]),
                    RANDNUM = random:uniform(),
                    if
                      RANDNUM < 0.05 ->
                        io:format("I, (~p), quit.~n", [self()]),
                        node_rec(MYNUM, "KnowDontTell", NUMNODES, VALUE, TRIES);
                      true ->
                        node_rec(MYNUM, STATUS, NUMNODES, (VALUE + THEIR_VALUE) / 2, TRIES)
                    end,
                    io:format("I, (~p), quit.~n", [self()]),
                    node_rec(MYNUM, "KnowDontTell", NUMNODES, VALUE, TRIES);
                  true ->
                    node_rec(MYNUM, STATUS, NUMNODES, (VALUE + THEIR_VALUE) / 2, TRIES)
                end;
              STATUS == "DontKnow" ->
                node_rec(MYNUM, "KnowAndTell", NUMNODES, (VALUE + THEIR_VALUE) / 2, TRIES);
              true ->
                node_rec(MYNUM, STATUS, NUMNODES, VALUE, TRIES)
            end
    %%% if no matching message has arrived within ExprT milliseconds
    after 100 ->
        %%%io:format("Try Again ~p~n", [self()]),
        node_tell(MYNUM, STATUS, NUMNODES, VALUE, TRIES + 1)
    end.

%%% Startup the System
start(1, TOTAL) ->
    random:seed(now()),
    STARTVALUE = random:uniform(TOTAL * 2),
    io:format("node1 has ~p~n", [STARTVALUE]),
    register(node1, spawn(prj_avg, node_tell, [1, "KnowAndTell", TOTAL, STARTVALUE, 0]));
start(N, TOTAL) ->
    random:seed(now()),
    STARTVALUE = random:uniform(TOTAL * 2),
    PID = spawn(prj_avg, node_tell, [N, "DontKnow", TOTAL, STARTVALUE, 0]),
    io:format("~p is node~p~n", [PID, N]),
    io:format("node~p has ~p~n", [N, STARTVALUE]),
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
