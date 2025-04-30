pdf转docx + pandoc转docx 均会出现乱码情况，两种均不可行，不要折腾这个方案。

一个可行的方案是完全使用latex，但是需要latex里面所有的latex代码都是pandoc“正确的”，实际情况是往往很难，而且ref.docx文件也很难符合心意。

另一个可行的方案是用markdown做主力，可以配合md2latex.py转latex，配合typro+pandoc转docx，好处是能保留绝大部分信息，坏处是pandoc导出的格式需要重新调整。不一样而需要手动调整。
