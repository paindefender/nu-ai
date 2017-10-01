; call (find_bucharest "city_name") 
(setq cities '(
        ("Bucharest"         ("Pitesti"             101    )         ("Fagaras"             211    )         ("Giurgiu"             90    )         ("Urziceni" 85    )    )
        ("Sibiu"             ("Arad"             140    )         ("Oradea"             151    )         ("Rimnicu Vilcea"     80    )         ("Fagaras" 99    )    )
        ("Pitesti"             ("Rimnicu Vilcea"     97    )         ("Craiova"             138    )         ("Bucharest"         101    )                            )
        ("Arad"             ("Zerind"             75    )         ("Sibiu"            140    )         ("Timisoara"         118    )                            )
        ("Craiova"             ("Dobreta"             120    )         ("Rimnicu Vilcea"     146    )         ("Pitesti"             138    )                            )
        ("Urziceni"         ("Bucharest"         85    )         ("Vaslui"             142    )         ("Hirsova"             98    )                            )
        ("Rimnicu Vilcea"     ("Craiova"             146    )         ("Sibiu"             80    )         ("Pitesti"             97    )                            )
        ("Oradea"             ("Zerind"             71    )         ("Sibiu"             151    )                                                            )
        ("Zerind"             ("Oradea"             71    )         ("Arad"             75    )                                                            )
        ("Timisoara"         ("Arad"             118    )         ("Lugoj"             111    )                                                            )
        ("Lugoj"             ("Timisoara"         111    )         ("Mehadia"             70    )                                                            )    
        ("Mehadia"             ("Lugoj"             70    )         ("Dobreta"             75    )                                                            )
        ("Dobreta"             ("Mehadia"             75    )         ("Craiova"             120    )                                                            )
        ("Fagaras"             ("Sibiu"            99    )         ("Bucharest"         211    )                                                            )
        ("Hirsova"             ("Urziceni"         98    )         ("Eforie"             86    )                                                            )
        ("Vaslui"             ("Urziceni"         142    )         ("Iasi"             92    )                                                            )
        ("Iasi"             ("Vaslui"             92    )         ("Neamt"             87    )                                                            )
        ("Neamt"             ("Iasi"             87    )                                                                                            )
        ("Eforie"             ("Hirsova"             86    )                                                                                            )
        ("Giurgiu"             ("Bucharest"         90    )                                                                                            )
    )
)

(setq straight '(
        ("Arad"             366    )
        ("Bucharest"         0    )
        ("Craiova"             160    )
        ("Dobreta"             242    )
        ("Eforie"             161    )
        ("Fagaras"             176    )
        ("Giurgiu"             77    )
        ("Hirsova"             151    )    
        ("Iasi"             226    )
        ("Lugoj"             244    )
        ("Mehadia"             241    )
        ("Neamt"             234    )
        ("Oradea"             380    )
        ("Pitesti"             100    )
        ("Rimnicu Vilcea"     193    )
        ("Sibiu"             253    )
        ("Timisoara"         329    )
        ("Urziceni"         80    )
        ("Vaslui"             199    )
        ("Zerind"             374    )
    )
)

(defun getsldentry (city slds)
	(cond
		((null slds) "NOT FOUND")
		((string= (car (car slds)) city)
			(car slds)
		)
		(t (getsldentry city (cdr slds)))
	)
)

(defun find_bucharest (st_city) ; takes starting city as an argument
	(setq frontier (list (append (getsldentry st_city straight) '(0) '(0))))
	(start_search frontier)
)

(defun start_search (frontier)
	(cond 
		((check_frontier frontier) t)
		(t (start_search (exp_frontier frontier)))
	)
)

(defun get-min (frontier min_val) ; set min-val to something like ("Dummy" 999999 999999 999999) 
  (cond ((null (car frontier)) min_val)
        ((< (+ (car (cdr (cdr (car frontier)))) (car (cdr (cdr (cdr (car frontier)))))) (+ (car (cdr (cdr min_val))) (car (cdr (cdr (cdr min_val)))))) (get-min (cdr frontier) (car frontier)))
        (t (get-min (cdr frontier) min_val)))
)
(defun frontier_min (frontier) (get-min frontier '("Dummy" 999999 999999 999999)))

(defun nodes_calculate (parent children)
	(cond ((not (null children))
		(setq path (+ (car (cdr (car children))) (car (cdr (cdr (cdr parent))))))
		(setf (car children) (append (car children) (list (car (cdr (getsldentry (car (car children)) straight))))))
		(setf (car children) (append (car children) (list path)))
		(nodes_calculate parent (cdr children))
		children
	))
)

(defun exp_frontier (frontier)
	;(format t "Expanding frontier...~%")
	(setq fr_min (frontier_min frontier))
	(format t "~A expanded...~%" fr_min) 
	(setq new_nodes (cdr (getsldentry (car fr_min) cities)))
	(append (remove fr_min frontier) (nodes_calculate fr_min (copy-list new_nodes)))
)

(defun check_frontier (frontier)
	(cond ((string= (car (frontier_min frontier)) "Bucharest") (format t "~A" (frontier_min frontier)) t))
)
