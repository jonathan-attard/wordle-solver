function expand_word(word)
{
    var ex_word = [];
    var i = 0;

    while (i < word.length)
    {
        var letter = word[i];
        if (word[i] == 'i' && word[i + 1] == 'e')
        {
            var letter = "ie";
            i += 1;
        }
        if (word[i] == 'I' && word[i + 1] == 'E')
        {
            var letter = "IE";
            i += 1;
        }
        if (word[i] == 'g' && word[i + 1] == 'ħ')
        {
            var letter = "għ";
            i += 1;
        }
        if (word[i] == 'G' && word[i + 1] == 'Ħ')
        {
            var letter = "GĦ";
            i += 1;
        }

        ex_word.push(letter);
        i += 1;
    }

    return ex_word;
}
function ex_toString(list_word)
{
    return list_word.join("");
}

function get_word_wt(hist, WTree)
{
    // console.log(hist);
    var temp_tree = WTree;

    for (let i=0; i<hist.length; i++)
    {
        var key = hist[i];
        // console.log(key);
        temp_tree = temp_tree[key];
    }

    // console.log(temp_tree);
    var word = Object.keys(temp_tree)[0];
    // console.log(word_chosen);
    // console.log(word);
    word = word.toLocaleUpperCase();
    word = expand_word(word);
    // console.log(word);
    // console.log("REUTRN");
    return word
}