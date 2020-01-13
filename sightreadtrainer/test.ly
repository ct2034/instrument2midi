#(set! paper-alist (cons '("my size" . (cons (* 1 in) (* 1 in))) paper-alist))

\paper {
  #(set-paper-size "my size")
}

{
  c'
}
