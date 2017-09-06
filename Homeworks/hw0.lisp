(defun HELLO () "HELLO WORLD") ;Task 1

(defun SUMELEMENTS (elements) 
	(eval (cons '+ elements))
) ;Task 2

(defun AVG (elements)
	(/ (SUMELEMENTS elements) (length elements))
) ;Task 3

(defun PRINTINREVERSEORDER (elements)
	(cond 
		((not (null elements)) 
			(print (car (reverse elements))) 
			(PRINTINREVERSEORDER (butlast elements)) 
		)
	)
) ;Task 4

(defun CONTAINSMYVALUE (elements val)
	(cond ((member val elements) "YES, IT DOES") (t "NO, IT DOES NOT"))
) ;Task 5

(defun issorted (elements)
	(or (endp elements) (endp (cdr elements))
		(and (<= (car elements) (cadr elements)) (issorted (cdr elements)))
	)
)
(defun ISMYLISTSORTED (elements)
	(cond
		((issorted elements) "YES, IT IS")
		(t "NO, IT IS NOT")
	)
) ;Task 6
