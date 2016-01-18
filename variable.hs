--Michal Badura
--Simple implementation of a calculator allowing rational expressions and variables
--Somehow I managed without using the parsing libraries
import Data.Char
import Data.List
import Control.Category hiding ((.))
import Data.List.Split
import qualified Data.Map as M

data VRArithExpr = Number Int | Plus VRArithExpr VRArithExpr | Mult VRArithExpr VRArithExpr | Rational VRArithExpr VRArithExpr | Variable String deriving (Show)

evalToRat :: VRArithExpr -> VRArithExpr
evalToRat (Number a) = Rational (Number a) (Number 1)
evalToRat (Plus a b) = addRat (evalToRat a) (evalToRat b)
evalToRat (Mult a b) = multRat (evalToRat a) (evalToRat b)
evalToRat (Rational a b) = Rational (Number $ eval a) (Number $ eval b)

addRat (Rational p q) (Rational a b) = Rational (Number (a'*q' + p'*b')) (Number (q'*b'))
    where
        p' = eval p
        q' = eval q
        a' = eval a
        b' = eval b

multRat (Rational p q) (Rational a b) = Rational (Number(a'*p')) (Number (q'*b'))
    where
        p' = eval p
        q' = eval q
        a' = eval a
        b' = eval b

multIntoRat a b = multRat (evalToRat a) (evalToRat b)
addIntoRat a b = addRat (evalToRat a) (evalToRat b)

eval :: VRArithExpr -> Int
eval (Number a) = a
eval (Plus a b) = eval a + eval b
eval (Mult a b) = eval a * eval b

-- greatest common divisor
euclid n 0 = n
euclid n m = euclid m (n `mod` m)

simplify (Rational (Number a) (Number b)) = Rational (Number a') (Number b')
    where
        k = euclid a b
        a' = a `div` k
        b' = b `div` k

showRat (Rational (Number a) (Number b)) = show a ++ "/" ++ show b
showRat (Number a) = show a

strip :: String -> String
strip [] = []
strip (s:ss)
    |isSpace s = strip ss
    |otherwise = s:(strip ss)

--how deep in parenthesis the element is
level :: String -> Int -> Int
level str n = levelHelper str n 0 0
    where
        levelHelper str n counter current
            |current == n = counter
            |str!!current == '(' = levelHelper str n (counter+1) (current+1)
            |str!!current == ')' = levelHelper str n (counter-1) (current+1)
            |otherwise = levelHelper str n counter (current+1)


--gets rid of unnecessary parenthesis around the expression
stripParens :: String -> String
stripParens str
    |head str == '(' && last str == ')' && (all ((>0) . (level str)) [2..length str - 2]) = stripParens (init . tail $ str)
    |otherwise = str

--getsPrecedence of operator with index n
getPrec str n
    |str!!n == '+' = level str n *3
    |str!!n == '*' = (level str n)*3 + 1
    |str!!n == '/' = (level str n)*3 + 2
    |otherwise = 100000000 --this is very hacky, but for now should be fine 

lowerPrecedence str m n
    |getPrec str m == getPrec str n = EQ
    |getPrec str m > getPrec str n = GT
    |otherwise = LT

--find index an operator with highest (actually programmed as lowest precedence)
findSplit :: String -> Int
findSplit str = minimumBy (lowerPrecedence str) [0..length str - 1]

splitStr :: String -> (Char, (String, String))
splitStr str = (str!!n, (take n str, drop (n+1) str))
    where n = findSplit str


--I detect ill-formatted expressions in this function
buildExpr :: String -> VRArithExpr
--no (-) before expressions, because there is no subtraction defined in the specification
buildExpr str
    |all isDigit str' = Number $ read str'
    |all (\c -> (isLetter c) || (c=='^') || (isDigit c)) str' = Variable str'
    |operator == '+' = Plus (buildExpr str1) (buildExpr str2)
    |operator == '*' = Mult (buildExpr str1) (buildExpr str2)
    |operator == '/' = Rational (buildExpr str1) (buildExpr str2)
    where 
        (operator, (str1, str2)) = splitStr str'
        str' = stripParens str
buildExpr ('-':'(':as) = error "expressions -(exp) are not permitted, sorry!"
buildExpr ('-':as)
    |all isDigit as = Number $ (-1) * read(as)
    |otherwise = error "Ill-formatted expression"
buildExpr "" = error "Ill-formatted expression"



fix :: String -> String
fix = stripParens . strip
--------------------------------------------------------
--determines if an expression contains variables
isPure :: VRArithExpr -> Bool
isPure (Number _) = True
isPure (Rational _ _) = True
isPure (Variable _) = False
isPure (Plus a b) = (isPure a) && (isPure b)
isPure (Mult a b) = (isPure a) && (isPure b)

--separates a sum into a list of vrexpressions
separate :: VRArithExpr -> [VRArithExpr]
separate expr = separateHelper expr []
    where
        separateHelper (Plus a b) exps = (separate a)++(separate b)++exps
        separateHelper e exps = e:exps 

--now we have expressions with possibly mult - let's evaluate the coefficients and make variables into a list
separateVariables expr = separateHelper expr (Number 1, [])
    where
        separateHelper (Mult a b) result = joinHelper (separateHelper a result) (separateHelper b result)
            where joinHelper (c1, l1) (c2,l2) = (multIntoRat c1 c2, l1++l2)
        separateHelper (Variable x) (c, ls) = (c, ls++[x])
        separateHelper expr (c, ls) = (multIntoRat c (evalToRat expr), ls)

varToTuple var
    |elem '^' var = (a,(read b)::Int)
    |otherwise = (var, 1)
        where [a,b] = splitOn "^" var


groupVars vars = sort $ M.toList (M.fromListWith (+) vars)

data PolyExpr = PolyExpr [([(String, Int)], VRArithExpr)] deriving(Show)

collect :: VRArithExpr -> PolyExpr
collect expr = terms''
    where
        terms = (map separateVariables) . separate $ expr
        terms' = map (\(coeff, vars) -> (groupVars $ map varToTuple vars, coeff)) terms --now we have dictionary of (sorted variables, coefficient)
        terms'' = PolyExpr $ M.toList (M.fromListWith addIntoRat terms')

showPolyExpr (PolyExpr pexp) = concat (intersperse "+" $ map turnIntoString pexp)
    where
        turnIntoString (vars, coeff) = (showRat $ simplify coeff) ++ (concat $ map (("*"++ ) . (\(v,a) -> v ++ "^" ++ show a)) vars)

--------------------------------------------------------



main :: IO ()
main = do
    getLine >>= (fix >>> buildExpr >>> collect >>> showPolyExpr >>> putStrLn)

test[1] = (showPolyExpr . collect . buildExpr $ "2*x+-3*x") == "-1/1*x^1"
test[2] = (showPolyExpr . collect . buildExpr $ "2*x+-3*x^2") == "2/1*x^1+-3/1*x^2"