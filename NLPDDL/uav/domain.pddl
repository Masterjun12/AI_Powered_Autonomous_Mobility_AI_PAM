(define (domain uav-extended)
  (:requirements :strips :typing :durative-actions)

  (:types
    uav
    location
    package
  )

  (:predicates
    (at ?u - uav ?l - location)           ; 드론의 현재 위치
    (flying ?u - uav)                     ; 드론이 비행 중인지
    (landed ?u - uav)                     ; 착륙 상태인지
    (holding ?u - uav ?p - package)       ; 물체를 들고 있는지
    (empty-hand ?u - uav)                 ; 손이 비어 있는지
    (delivered ?p - package)              ; 물체가 배달 완료되었는지
  )

  ;; ------------------------------
  ;; [1] 이륙
  ;; ------------------------------
  (:action takeoff
    :parameters (?u - uav ?l - location)
    :precondition (and (at ?u ?l) (landed ?u))
    :effect (and (flying ?u) (not (landed ?u)))
  )

  ;; ------------------------------
  ;; [2] 이동 (직선)
  ;; ------------------------------
  (:action go
    :parameters (?u - uav ?from - location ?to - location)
    :precondition (and (at ?u ?from) (flying ?u))
    :effect (and (not (at ?u ?from)) (at ?u ?to))
  )

  ;; ------------------------------
  ;; [3] 착륙
  ;; ------------------------------
  (:action land
    :parameters (?u - uav ?l - location)
    :precondition (and (at ?u ?l) (flying ?u))
    :effect (and (landed ?u) (not (flying ?u)))
  )

  ;; ------------------------------
  ;; [4] 물체 줍기
  ;; ------------------------------
  (:action pickup
    :parameters (?u - uav ?p - package ?l - location)
    :precondition (and
      (at ?u ?l)
      (at ?p ?l)
      (landed ?u)
      (empty-hand ?u)
    )
    :effect (and
      (holding ?u ?p)
      (not (empty-hand ?u))
      (not (at ?p ?l))
    )
  )

  ;; ------------------------------
  ;; [5] 물체 내려놓기
  ;; ------------------------------
  (:action drop
    :parameters (?u - uav ?p - package ?l - location)
    :precondition (and
      (at ?u ?l)
      (landed ?u)
      (holding ?u ?p)
    )
    :effect (and
      (at ?p ?l)
      (delivered ?p)
      (empty-hand ?u)
      (not (holding ?u ?p))
    )
  )

  ;; ------------------------------
  ;; [6] 회전 (시계/반시계)
  ;; ------------------------------
  (:action rotate
    :parameters (?u - uav ?deg - location)
    :precondition (flying ?u)
    :effect (flying ?u)
  )
)
