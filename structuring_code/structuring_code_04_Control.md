# Control
When a program runs one needs to have some control over evaluation.  
Code in the `Setup` | `Basics` | `Set_Ops` section have so far only required running MM2 for a very limited number of iterations.  
Despite this we have exerted a minor amount of "control" over the evaluation of our programs.  

With the advent of structured programming it was established that control flow for algorithms can understood through the lens of three major control constructs
- Sequence
- Selection
- Iteration

We will not pretend that MM2 is a "structured programming language" (MM2 is more in the family of process calculi), but we will use structured programming as means of comparison, and when useful find means to emulate it.

## Sequence
Sequencing in MM2 can be done with a combination of two properties:
- priority
- execs that spawn execs

### Priority Sequencing
Priority dictate which exec to run first.

Given the following program:
```
(exec 1 (, $x) (, 1))
(exec 0 (, $x) (, 0))
(exec 3 (, $x) (, 3))
(exec 2 (, $x) (, 2))
```

An ordering of all the priorities can be done from 0 to 3.
Each has been hardcoded to write out their priorities when they successfully execute.

run for all steps in 0 to 3 inclusive
```sh
./mork run --steps 0 Control_01_Priority_Seq.mm2
./mork run --steps 1 Control_01_Priority_Seq.mm2
./mork run --steps 2 Control_01_Priority_Seq.mm2
./mork run --steps 3 Control_01_Priority_Seq.mm2
```

Using the MORK CLI as we have so far, the ordering is deterministic. For each step amount, the writes will sequence in the expected way.
### Execs chain sequencing
Another way to Sequence operations is to have an exec spawn another exec as one of it's outputs.
```
(exec 0 (, $x)
        (, 0
           (exec 0 (, 0)
                   (, 1
                      (exec 0 (, 1) 
                              (, 2
                                 (exec 0 (, 2)
                                         (, 3)
                                 )
                              )
                      )
                   )
           )
        )
)
```

Here each exec writes a value, spawns the next.
Each exec will run if the patterns succeed:
- the first one will succeed as it matches itself
- The ones that follow will succeed as they match the value of the previous write.
run for all steps in 0 to 3 inclusive
```sh
./mork run --steps 0 Control_02_Exec_Chaining_Seq.mm2
./mork run --steps 1 Control_02_Exec_Chaining_Seq.mm2
./mork run --steps 2 Control_02_Exec_Chaining_Seq.mm2
./mork run --steps 3 Control_02_Exec_Chaining_Seq.mm2
``` 

This causes a sequencing. The exact method of generating an exec (by hardcoding, or matching a "definition") does not matter.
In contrast to priorities, the ordering is _dependant_ on a previous exec successfully running.
We can modify the code such that a spawned exec fails to match (in this case instead of it will fail to find `!`).
```
(exec 0 (, $x)
        (, 0
           (exec 0 (, !)
                   (, 1
                      (exec 0 (, !)
                              (, 2
                                 (exec 0 (, !)
                                         (, 3)
                                 )
                              )
                      )
                   )
           )
        )
)
```
run for all steps in 0 to 1 inclusive.
```sh
./mork run --steps 0 Control_03_Exec_Chaining_Fail_Seq.mm2
./mork run --steps 1 Control_03_Exec_Chaining_Fail_Seq.mm2
``` 
The first exec will run, but the second one will fail, and disappear.
## Selection
Execs have a built in means of selection via pattern matching.
```
(case b)
(case c)
(exec 0 (, (case a)) (, a))
(exec 0 (, (case b)) (, b))
(exec 0 (, (case c)) (, c))
```
run `./mork run Control_04_Select_b_c.mm2`

We can try to run all cases, and we select `(case b)` and `(case c)`.

An alternative would be to "match first".
There are dual ways of doing this.
The first is to remove the data that would be matched.
```
(case b)
(case c)
(exec 0 (, (case a) (case $x)) (O (+ a) (- (case $x) )))
(exec 0 (, (case b) (case $x)) (O (+ b) (- (case $x) )))
(exec 0 (, (case c) (case $x)) (O (+ c) (- (case $x) )))
```
run `./mork run Control_05_Select_First_Data.mm2`
outputs `b`
The other would be to remove the execs that would match.
```
(case b)
(case c)
(exec 0 (, (case a) (exec 0 $p $t)) (O (+ a) (- (exec 0 $p $t) )))
(exec 0 (, (case b) (exec 0 $p $t)) (O (+ b) (- (exec 0 $p $t) )))
(exec 0 (, (case c) (exec 0 $p $t)) (O (+ c) (- (exec 0 $p $t) )))


(exec 1 (, $x) (, (Ran After)))
```
run `./mork run Control_06_Select_First_Exec.mm2`
An extra exec has been added to show that we only removed execs of a given priority.
outputs:
```
(Ran After)
(case b)
(case c)
b
```

## Iteration
Making an infinite loop is not very hard, we just need the exec that keeps constructing itself.
```
(exec 0 (, (exec 0 $p $t) )
        (, (exec 0 $p $t) )
)
```
run `./mork run --steps 0 Control_07_Recursive.mm2`
This exec unifies with itself ....
```
MGU : {
   $p0 => (, (exec 0 $p1 $t1) )
   $t0 => (, (exec 0 $p1 $t1) )
}
```
then templates itself.
```
(, (exec 0 $p0 $t0) )
=>
(, (exec 0 (, (exec 0 $p1 $t1) ) (, (exec 0 $p1 $t1) )) )
```
We get the same exec back.
Iteration was done using recursion, on closer inspection we see that recursion was done by our second sequencing technique, exec chaining.
In some sense the actual thing iterating is the runtime itself.
## Halt Iteration with Sequencing and Selection
The issue is that we want most sub-programs to halt. We can do this by selection failure. Selection failure exhausts the exec, ending the loop.
We do so below by decrementing a counter (here with Peano arithmetic).
```
(counter (S (S (S Z))))
(exec LOOP (, (counter (S $N))
              (exec LOOP $p $t)
           )
           (O  (+ (exec LOOP $p $t)   ) 
               (+ (counter $N)     )
               (- (counter (S $N)) )
           )
)
```
run `./mork run --steps 0 Control_08_Halts_on_fail.mm2`

you should find this.
```
(counter (S (S Z)))
(exec LOOP (, (counter (S $a)) (exec LOOP $b $c)) (O (+ (exec 0 $b $c)) (+ (counter $a)) (- (counter (S $a)))))
```
the counter decremented by one Peano successor.
Every time we sequence by chaining the exec, we modify the state such that we converge to failure.
When the match fails at `(counter Z)`, the exec will be exhausted without making any writes, so it won't write itself back
Another alternative is to spawn other execs with higher priority, and it have one exec be responsible for termination. It would run every in an unbounded way, expecting one of the spawned execs to fail until it matches; that exec would then be responsible to remove the looping exec.
Initialize the loop
```
(counter (S (S (S Z))))
(exec (LOOP 9) 
   (, (exec (LOOP 9) $p $t) )
   (O <...things to spawn> 
   )
)
```

High priority conditional break:
```
(+ (exec (LOOP 0) 
     (, (exec (LOOP $n) $_p $_t)
        (counter Z) 
     )
     (O (- (exec (LOOP $n) $_p $_t) ))
   )
)
```

Lower priority action:
```
(+ (exec (LOOP 1) 
     (, (counter (S $x)) ) 
     (O 
        (+ (counter $x)     )
        (- (counter (S $x)) )
     )
   )
)

```

Low priority infinite loop:
```
(+ (exec (LOOP 9) $p $t))
```
run `./mork run Control_09_Halts_on_success.mm2`

----

Some of these patterns need to be modified when doing multithreading, but it should be sufficient for following the rest of the tutorial.
If one is interested in some of the considerations about that, have a look at the `structuring_code/WIP/structuring_code_XX_Multithreading.md` file (it's work in progress).

----

Next we start building a more involved program in [`structuring_code_05_Going_Wide.md`](https://github.com/ClarkeRemy/MM2_Structuring_Code/blob/main/structuring_code/structuring_code_05_Going_Wide.md).
