
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <stdint.h>

typedef enum
{
    Task_Decode = 0,
    Task_Encode = 1,
} Task_t;

typedef enum
{
    false = 0,
    true = 1
} Bool_t;

static const char set[] =
{
    'a', 'b', 'c', 'd', 'e', 'f',
    'g', 'h', 'i', 'j', 'k', 'l',
    'm', 'n', 'o', 'p', 'q', 'r',
    's', 't', 'u', 'v', 'w', 'x',
    'y', 'z'
};

typedef struct
{
    char alphabet[sizeof(set)];
    char *current;
    char *end;
} Encoder_Context;

static Bool_t
isAlpha(
    char letter);

static Bool_t
isUpper(
    char letter);

static char
toLower(
    char letter);

static Bool_t
parseKey(
    const char *key);

static Bool_t
isValid(
    char letter);

static uint8_t
lookupIndex(
    char letter);

static int
rotate(
    char letter,
    Encoder_Context *ctx);

static char
encode(
    char letter,
    Encoder_Context *ctx);

static uint8_t
reverseLookup(
    char letter,
    Encoder_Context *ctx);

static char
decode(
    char letter,
    Encoder_Context *ctx);

static int
init(
    const char *key,
    Encoder_Context *ctx);

static Bool_t
isAlpha(
    char letter)
{
    if (letter >= 'A' && letter <= 'Z')
    {
        return true;
    }

    if (letter >= 'a' && letter <= 'z')
    {
        return true;
    }

    return false;
}

static Bool_t
isUpper(
    char letter)
{
    if (letter >= 'A' && letter <= 'Z')
    {
        return true;
    }

    return false;
}

static char
toLower(
    char letter)
{
    if (isUpper(letter))
    {
        letter += 0x20;
    }

    return letter;
}

static Bool_t
parseKey(
    const char *key)
{
    size_t keyLen, i;

    if (NULL == key)
    {
        return false;
    }

    keyLen = strlen(key);

    for (i = 0; i < keyLen; i++)
    {
        if (!isValid(key[i]))
        {
            return false;
        }
    }

    return true;
}

static Bool_t
isValid(
    char letter)
{
    if (letter >= set[0] && letter <= set[sizeof(set)-1])
    {
        return true;
    }

    return false;
}

static uint8_t
lookupIndex(
    char letter)
{
    return (letter - set[0]);
}

static int
rotate(
    char letter,
    Encoder_Context *ctx)
{
    uint8_t indx = lookupIndex(letter);
    uint32_t i;
    char move;

    if (indx > sizeof(ctx->alphabet))
    {
        return -1;
    }

    move = ctx->alphabet[indx];

    for (i = indx; i < (sizeof(ctx->alphabet) - 1); i++)
    {
        ctx->alphabet[i] = ctx->alphabet[i+1];
    }

    ctx->alphabet[sizeof(ctx->alphabet) - 1] = move;

    return 0;
}

/**
 * @brief This takes a letter and encodes it.
 *
 * This process is fairly straightforward.  It does a lookup
 * of where the letter would normally occur and then goes to that position
 * in ctx->alphabet given the starting point of ctx->current.
 *
 * ctx->current is then updated to reflect that the starting point in the
 * alphabet has now changed.  (>= end).
 */
static char
encode(
    char letter,
    Encoder_Context *ctx)
{
    char ret;
    uint8_t indx = lookupIndex(letter);
    uint8_t ofs;

    /* if the indx is beyond where we are, the therefore behind current */
    if (indx >= (ctx->end - ctx->current))
    {
        ofs = indx - (ctx->end - ctx->current);

        ret = ctx->alphabet[ofs];
    }
    else
    {
        ret = ctx->current[indx];
    }

    /* adjust substitution table */
    ctx->current += 1;

    if (ctx->current >= ctx->end)
    {
        ctx->current = ctx->alphabet;
    }

    return ret;
}

static uint8_t
reverseLookup(
    char letter,
    Encoder_Context *ctx)
{
    uint8_t i;

    for (i = 0; i < sizeof(ctx->alphabet); i++)
    {
        if (letter == ctx->alphabet[i])
        {
            return i;
        }
    }

    return -1;
}

static char
decode(
    char letter,
    Encoder_Context *ctx)
{
    /* need to do reverse look up and where it is in
     * comparison to the current
     * can impact some stuff.
     */
    uint8_t indx = reverseLookup(letter, ctx);
    uint8_t ofs;
    char ret;

    /* it is not wrapped around */
    if (&(ctx->alphabet[indx]) > ctx->current)
    {
        ret = set[&(ctx->alphabet[indx]) - ctx->current];
    }
    else if (&(ctx->alphabet[indx]) < ctx->current)
    {
        ofs = ctx->end - ctx->current;
        ret = set[indx + ofs];
    }
    else
    {
        ret = set[0];
    }

    ctx->current += 1;

    if (ctx->current >= ctx->end)
    {
        ctx->current = ctx->alphabet;
    }

    return ret;
}

static void
dumpAlphabet(
    const char *alphabet,
    uint32_t    alphaLen)
{
    uint32_t i;

    if (NULL == alphabet)
    {
        return;
    }

    for (i = 0; i < alphaLen; i++)
    {
        printf("%c", alphabet[i]);
    }

    printf("\n");

    return;
}

static int
init(
    const char *key,
    Encoder_Context *ctx)
{
    size_t keyLen;
    uint32_t i;

    if (NULL == key || NULL == ctx)
    {
        return -1;
    }

    bzero(ctx, sizeof(Encoder_Context));

    /* these are the same size */
    memcpy(ctx->alphabet, set, sizeof(set));

    ctx->current = ctx->alphabet;
    ctx->end = ctx->alphabet + sizeof(ctx->alphabet);

    keyLen = strlen(key);

    printf("0: ");
    dumpAlphabet(ctx->alphabet, sizeof(ctx->alphabet));

    /* okay, now rotate the substitution table by the key */
    for (i = 0; i < keyLen; i++)
    {
        if (rotate(key[i], ctx))
        {
            return -1;
        }

        printf("%c: ", key[i]);
        dumpAlphabet(ctx->alphabet, sizeof(ctx->alphabet));
    }

    return 0;
}

static void
ioerror(const char *filename)
{
    if (NULL == filename)
    {
        return;
    }

    fprintf(stderr, "ioerror: '%s'\n", filename);

    return;
}

static void
usage(void)
{
    fprintf(stderr, "usage: ./encoder (-e|-d) -k key -if input -cf clean -of output\n");

    return;
}

#define BUFFER_LEN 1024

int main(int argc, char *argv[])
{
    FILE *ifp, *ofp, *cfp;
    Encoder_Context context;
    Task_t task = -1;
    const char *key = NULL;
    const char *input_fname = NULL;
    const char *clean_fname = NULL;
    const char *output_fname = NULL;
    char *cmd;
    size_t cmdLen, bytesRead;
    uint32_t i;
    char inputBuf[BUFFER_LEN], cleanBuf[BUFFER_LEN];

    /* verify parameters */
    if (argc < 8)
    {
        usage( );
        exit(-1);
    }

    for (i = 0; i < argc; i++)
    {
        cmd = argv[i];
        cmdLen = strlen(cmd);

        if (strncmp("-d", cmd, cmdLen) == 0)
        {
            printf("decoding\n");
            task = Task_Decode;
        }
        else if (strncmp("-e", cmd, cmdLen) == 0)
        {
            printf("encoding\n");
            task = Task_Encode;
        }
        else if (strncmp("-k", cmd, cmdLen) == 0)
        {
            key = argv[i+1];
            printf("key = '%s'\n", key);
        }
        else if (strncmp("-if", cmd, cmdLen) == 0)
        {
            input_fname = argv[i+1];
            printf("input = '%s'\n", input_fname);
        }
        else if (strncmp("-cf", cmd, cmdLen) == 0)
        {
            clean_fname = argv[i+1];
            printf("clean = '%s'\n", clean_fname);
        }
        else if (strncmp("-of", cmd, cmdLen) == 0)
        {
            output_fname = argv[i+1];
            printf("output = '%s'\n", output_fname);
        }
    }

    /* required params */
    if (NULL == key || NULL == input_fname || NULL == output_fname || -1 == task)
    {
        fprintf(stderr, "missing or invalid required parameter\n");
        exit(-1);
    }

    if (Task_Encode == task && NULL == clean_fname)
    {
        fprintf(stderr, "you need to specify a clean output file when encoding\n");
        exit(-1);
    }

    /* set up key stuff */
    if (!parseKey(key))
    {
        fprintf(stderr, "invalid key\n");
        exit(-1);
    }

    if (init(key, &context))
    {
        fprintf(stderr, "could not setup thing\n");
        exit(-1);
    }

    /* run through file */
    ifp = fopen(input_fname, "r");

    if (NULL == ifp)
    {
        ioerror(input_fname);
        exit(-2);
    }

    if (Task_Encode == task)
    {
        cfp = fopen(clean_fname, "w");

        if (NULL == cfp)
        {
            ioerror(clean_fname);
            exit(-2);
        }
    }

    ofp = fopen(output_fname, "w");

    if (NULL == ofp)
    {
        ioerror(output_fname);
        exit(-2);
    }

    /* process the text file */
    while (!feof(ifp))
    {
        bzero(inputBuf, sizeof(inputBuf));
        bzero(cleanBuf, sizeof(cleanBuf));

        bytesRead = fread(inputBuf, sizeof(char), sizeof(inputBuf), ifp);

        for (i = 0; i < bytesRead; i++)
        {
            switch (task)
            {
                case Task_Encode:

                    cleanBuf[i] = inputBuf[i];

                    if (isAlpha(inputBuf[i]))
                    {
                        cleanBuf[i] = toLower(inputBuf[i]);
                        inputBuf[i] = encode(cleanBuf[i], &context);
                    }

                    break;

                case Task_Decode:

                    if (isValid(inputBuf[i]))
                    {
                        inputBuf[i] = decode(inputBuf[i], &context);
                    }

                    break;

                default:
                    break;
            } /* end switch */
        } /* for each byte */

        if (Task_Encode == task)
        {
            fwrite(cleanBuf, sizeof(char), bytesRead, cfp);
        }

        fwrite(inputBuf, sizeof(char), bytesRead, ofp);
    } /* while !eof */

    if (Task_Encode == task)
    {
        fclose(cfp);
    }

    fclose(ifp);
    fclose(ofp);

    return 0;
}
