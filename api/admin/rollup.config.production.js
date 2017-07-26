import resolve from 'rollup-plugin-node-resolve';
import babel from 'rollup-plugin-babel';
import filesize from 'rollup-plugin-filesize';
import progress from 'rollup-plugin-progress';
import cleanup from 'rollup-plugin-cleanup'; // production

export default {
  entry: './admin/scripts/app.js',
  dest: './admin/static/bundle.js',
  format: 'cjs',
  plugins: [
    cleanup(),
    resolve(),
    babel({
      exclude: 'node_modules/**'
    }),
    filesize(),
    progress(),

  ],
  sourceMap: false
};
