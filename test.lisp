
(def std (make-env *env*))

(with-env std
  (load-file "std.lisp"))

(println 'pi: (with-env std pi))

(load-file "std.lisp")

(println (unless nil 'a))
