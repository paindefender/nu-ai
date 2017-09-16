; Documentation
; For unweighted trees:
; 	* (print_tree tree) for printing in DFS order
;	* (print_tree_bfs tree) for printing in BFS order
;	* (search_tree tree start_node switch) for searching
;		switch takes one of two values:
;			* 0 - BFS ordering
;			* 1 - DFS ordering
;
;	Examples:
;		(print_tree '(A (B (J)) (C (F) (R (M))) (D (L))))
;		(print_tree_bfs '(A (B (J)) (C (F) (R (M))) (D (L))))
;		(search_tree '(A (B (J)) (C (F) (R (M))) (D (L))) 'C 0)
;
; For weighted trees:
;	* (print_tree_w tree) for printing in DFS order
;
;	Examples:
;		(print_tree_w '((a 0) ((b 3) ((d 1)) ((e 2) ((h 3)) ((i 5))) ((f 3))) ((c 4) ((g 4)))))

; tree printing dfs functions
(defun print_children (tree)
	(cond 	
		((not (null tree)) 
			(format t " ~A " (car (car tree)))
			(print_children (cdr tree))
		)
		(t (format t "|~%"))
	)
)
(defun use_children (tree)
	(cond
		((not (null tree))
			(print_tree (car tree))
			(use_children (cdr tree))
		))
)
(defun print_tree (tree) 
	(cond 	
		((not (null tree)) 
			(format t "> ~A" (car tree))
			(format t " --> |")
			(print_children (cdr tree))
			(use_children (cdr tree))
		))
)
; tree printing dfs end

; tree printing bfs functions
(defun trim_first (tree)
	(cond 
		((not (null (cdr (car tree)))) 
			(cons (remove_parentheses (cdr (car tree))) (trim_mod (cdr tree)))
		)
		((not (null (cdr tree)))
			(trim_mod (cdr tree))
		)
		(t 
			nil
		)
	)
)
(defun trim_mod(tree)
	(cond 
		((listp (car (remove_parentheses tree)))
			(trim_first (remove_parentheses tree))
		)
		(t (trim_first tree))
	)
)
(defun remove_parentheses (tree)
	(cond
		(( not (atom (car tree)))
			(cond 
				((not (<= (list-length tree) (list-length (car tree)))) 
					tree
				)
				(t (remove_parentheses (car tree)))
			)
		)
		(t 
			tree
		)
	)
)
(defun print_tree_bfs (tree)
	(format t "~A --> |" (car tree))
	(print_children (cdr tree))
	(format t "going deeper~%")
	(bfs_print (cdr tree))
)
(defun bfs_print (nodes)
	(cond
		((not (null nodes))
			(children_printer_helper nodes)
			(format t "going deeper~%")
			(bfs_print (trim_mod nodes))
		)
	)
)
(defun children_printer_helper (nodes)
	(cond 
		((not (null (car nodes)))
			(cond 
				((listp (car (car nodes)))
					(children_printer_helper (car nodes))
					(children_printer_helper (cdr nodes))
				)
				(t 
					(format t "~A --> |" (car (car nodes)))
					(print_children (cdr (car nodes)))
					(children_printer_helper (cdr nodes))
				)
			)
		)
	)
)
; tree printing bfs end

;tree searching functions
(defun search_tree (tree start switch)
	(cond 
		((= switch 0)
			(print_tree_bfs (print_tree_f tree start))
		)
		((= switch 1)
			(print_tree (print_tree_f tree start))
		)
		(t (print "Switch should be either 0(bfs) or 1(dfs)"))
	)
)
(defun print_children_f (tree node)
	(cond
		((not (null tree)) 
			(print_children_f (cdr tree) node)
		)
	)
)
(defun use_children_f (tree node)
	(cond
		((not (null tree))
			(cond 
				((not (null (print_tree_f (car tree) node)))
					(print_tree_f (car tree) node)
				)
				(t 
					(use_children_f (cdr tree) node)
				)
			)
			
		))
)
(defun print_tree_f (tree node) 
	(cond 	
		((not (null tree)) 
			(cond 
				((eq (car tree) node)
					tree
				)
				(t 
					(print_children_f (cdr tree) node)
					(use_children_f (cdr tree) node)
				)
			)
		))
)
;tree searching functions end

;dfs printing for weighted trees
(defun print_children_w (tree)
	(cond 	
		((not (null tree)) 
			(format t " ~A " (car tree))
			(print_children_w (cdr tree))
		)
		(t (format t "|~%"))
	)
)
(defun use_children_w (tree)
	(cond
		((not (null tree))
			(print_tree_w (car tree))
			(use_children_w (cdr tree))
		))
)
(defun print_tree_w (tree) 
	(cond 	
		((not (null tree)) 
			(format t "> ~A" (car tree))
			(format t " --> |")
			(print_children_w (cdr tree))
			(use_children_w (cdr tree))
		))
)
