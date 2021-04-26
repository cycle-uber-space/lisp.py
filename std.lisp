
(def pi 3.141592654)

(defun not (arg)
  (if arg
      nil
      t))

(defmacro progn body
  ;; TODO use backquote
  ;;`(lambda () ,@body)
  (cons (cons 'lambda (cons '() body)) nil))

(defmacro when (test . body)
  (cons 'if (cons test (cons (cons 'progn body) nil))))

(defmacro unless (test . body)
  (cons 'when (cons (cons 'not (cons test nil)) body)))
