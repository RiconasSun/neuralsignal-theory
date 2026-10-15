"""Public-input membership guard; not a signer or secret-scalar implementation.

Encoding/extended Edwards arithmetic: RFC8032 sections5.1.3 and6.
The extra nonidentity/[L]P condition enforces prime-order authority keys.
"""
P=2**255-19
L=2**252+27742317777372353535851937790883648493
D=(-121665*pow(121666,P-2,P))%P
SQRT_MINUS_ONE=pow(2,(P-1)//4,P)
VALIDATION_POLICY='ED25519_CANONICAL_PRIME_SUBGROUP_V1'

def _add(a,b):
    minus=(a[1]-a[0])*(b[1]-b[0])%P
    plus=(a[1]+a[0])*(b[1]+b[0])%P
    cross=2*D*a[3]*b[3]%P
    scale=2*a[2]*b[2]%P
    e,f,g,h=plus-minus,scale-cross,scale+cross,plus+minus
    return (e*f%P,g*h%P,f*g%P,e*h%P)

def _multiply(point,scalar):
    result=(0,1,1,0)
    while scalar:
        if scalar&1:result=_add(result,point)
        point=_add(point,point);scalar>>=1
    return result

def validate_public_point(raw):
    if not isinstance(raw,bytes) or len(raw)!=32:raise PermissionError('ED25519_PUBLIC_LENGTH')
    encoded=int.from_bytes(raw,'little');sign=encoded>>255;y=encoded&((1<<255)-1)
    if y>=P:raise PermissionError('ED25519_NONCANONICAL_Y')
    yy=y*y%P;denominator=(D*yy+1)%P
    if not denominator:raise PermissionError('ED25519_OFF_CURVE_DENOMINATOR')
    square=(yy-1)*pow(denominator,P-2,P)%P
    x=pow(square,(P+3)//8,P)
    if x*x%P!=square:x=x*SQRT_MINUS_ONE%P
    if x*x%P!=square:raise PermissionError('ED25519_OFF_CURVE')
    if x==0 and sign:raise PermissionError('ED25519_NONCANONICAL_X_SIGN')
    if x&1!=sign:x=P-x
    if (-x*x+yy-1-D*x*x*yy)%P:raise PermissionError('ED25519_OFF_CURVE')
    if (y|((x&1)<<255)).to_bytes(32,'little')!=raw:raise PermissionError('ED25519_NONCANONICAL_ENCODING')
    if x==0 and y==1:raise PermissionError('ED25519_IDENTITY_PUBLIC_KEY')
    result=_multiply((x,y,1,x*y%P),L)
    if result[2]%P==0 or result[0]%P!=0 or (result[1]-result[2])%P!=0:raise PermissionError('ED25519_NOT_PRIME_SUBGROUP')
    return raw
