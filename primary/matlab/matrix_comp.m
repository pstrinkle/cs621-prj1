% Matrix completion demo

%rng(234923);    % for reproducible results
X            = x1
[rows, cols] = size(X)
N            = rows * cols
r            = 2;        % the rank of the matrix
nSamples     = N / 2; % number of observed entries

% For this demo, we will use a matrix with integer entries
% because it will make displaying the matrix easier.
iMax         = 5;

%Let “Omega” be the set of observed entries

rPerm   = randperm(N); % use "randsample" if you have the stats toolbox
omega   = sort( rPerm(1:nSamples) );

% Show the observed data
Y = nan(N);
Y(omega) = X(omega);
disp('The "NaN" entries represent unobserved values');
disp(Y)

% Run the completion code
observations = X(omega);    % the observed entries
mu           = .001;        % smoothing parameter

% The solver runs in seconds
tic
Xk = solver_sNuclearBP( {row,col,omega}, observations, mu );
toc

% Show the recovered data

disp('Recovered matrix (rounding to nearest .0001):')
disp( round(Xk*10000)/10000 )
% and for reference, here is the original matrix:
disp('Original matrix:')
disp( X )

% The relative error (without the rounding) is quite low:
fprintf('Relative error, no rounding: %.8f%%\n', norm(X-Xk,'fro')/norm(X,'fro')*100 );
