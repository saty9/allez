var gulp        = require('gulp');
var browserSync = require('browser-sync');
var reload      = browserSync.reload;

gulp.task('browsersync', function() {
    browserSync.init({
        notify: false,
        proxy: "127.0.0.1:8000"
    });
    gulp.watch(['./**/*.{scss,css,html,py,js}'], reload);
    gulp.watch(['./**/*.hbs'], ['handlebars']);
});


var uglify = require('gulp-uglify');            // minify js file
var handlebars = require('gulp-handlebars');    // compile handlebar templates
var defineModule = require('gulp-define-module');
var declare = require('gulp-declare');
var rename = require('gulp-rename');

gulp.task('handlebars', function(){
  gulp.src('ui/static/ui/templates/src/*.hbs')
    .pipe(handlebars())
    .pipe(defineModule('plain'))
    .pipe(declare({
      namespace: 'Handlebars.templates'
    }))
    .pipe(rename({ extname: '.js' }))
    .pipe(uglify())
    .pipe(gulp.dest('ui/static/ui/templates'));
});