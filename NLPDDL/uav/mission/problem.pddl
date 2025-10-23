```pddl
(define (problem mission-1)
  (:domain uav)
  (:objects
    loc-start - location
    loc-200m - location
  )
  (:init
    (at loc-start)
    (is-gnd)
    (= (distance loc-start loc-200m) 200)
    (= (distance loc-200m loc-start) 200)
  )
  (:goal
    (and
      (at loc-200m)
      (is-gnd)
    )
  )
)
```