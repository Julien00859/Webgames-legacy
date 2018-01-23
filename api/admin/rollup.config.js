import resolve from 'rollup-plugin-node-resolve';
import babel from 'rollup-plugin-babel';
import commonjs from 'rollup-plugin-commonjs';
import filesize from 'rollup-plugin-filesize';
import progress from 'rollup-plugin-progress';

export default {
  entry: './admin/scripts/app.js',
  dest: './admin/static/bundle.js',
  format: 'cjs',
  plugins: [
    resolve(),
    commonjs(),
    babel({
      exclude: '../node_modules/**'
    }),
    filesize(),
    progress()
  ],
  sourceMap: true
};
