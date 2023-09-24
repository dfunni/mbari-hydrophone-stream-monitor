from flask import Flask, render_template, request

from cetacean import DataDir, MarsClip, get_data

app = Flask(__name__)


@app.route("/")
def plot():
    # Generate the figure **without using pyplot**.
    my_clip = MarsClip("/data/whale/20230920_002717Z.mp3")
    data = my_clip.get_spec_img_data()
    fname = my_clip.get_filename()
    fpath = my_clip.get_filepath()
    return render_template('index.html', filename=fname, filepath=fpath, img_data=data)


@app.route("/", methods=['GET', 'POST'])
def buttons():
    if request.method == 'POST':
        if request.form.get('whale') == 'Whale':
            pass # do something
        elif  request.form.get('no_whale') == 'No Whale':
            pass # do something else
        else:
            pass # unknown
    elif request.method == 'GET':
        return render_template('index.html', form=form)
    
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)