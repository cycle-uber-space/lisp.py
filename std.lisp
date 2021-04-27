
;;(def pi 3.141592654)

(def not (lambda (arg) (if arg nil t)))

(def defun (syntax (name args . body)
             `(def ,name (lambda ,args ,@body))))

(def defmacro (syntax (name args . body)
                `(def ,name (syntax ,args ,@body))))

;;(defun not (arg)
;;  (if arg
;;      nil
;;      t))

(defun append (a b)
  (if a
      (cons (car a)
            (append (cdr a) b))
      b))

(defun list args
  (append args nil))

(defmacro progn body
  ;; TODO use backquote
  ;;`(lambda () ,@body)
  (list (cons 'lambda (cons '() body))))

(defmacro when (test . body)
  (cons 'if (cons test (list (cons 'progn body)))))

(defmacro unless (test . body)
  (cons 'when (cons (cons 'not (list test)) body)))
