"""
CTE Form 29 Data Models
=======================
"""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import field as dc_field
from datetime import date
from typing import (
    Any,
    ClassVar,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from cl_sii.rcv.data_models import PeriodoTributario
from cl_sii.rut import Rut


logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class CteForm29NaturalKey:
    contribuyente_rut: Rut
    periodo_tributario: PeriodoTributario
    folio: int


@dataclasses.dataclass(frozen=True)
class CteForm29:
    contribuyente_rut: Rut
    periodo_tributario: PeriodoTributario
    folio: int

    apellido_paterno_o_razon_social: Optional[str] = dc_field(default=None, repr=False)
    apellido_materno: Optional[str] = dc_field(default=None, repr=False)
    nombres: Optional[str] = dc_field(default=None, repr=False)
    calle_direccion: Optional[str] = dc_field(default=None, repr=False)
    numero_direccion: Optional[str] = dc_field(default=None, repr=False)
    comuna_direccion: Optional[str] = dc_field(default=None, repr=False)
    telefono: Optional[str] = dc_field(default=None, repr=False)
    correo_electronico: Optional[str] = dc_field(default=None, repr=False)
    representante_legal_rut: Optional[Rut] = dc_field(default=None, repr=False)

    total_a_pagar_en_plazo_legal: Optional[int] = dc_field(default=None, repr=False)
    total_a_pagar_con_recargo: Optional[int] = dc_field(default=None, repr=False)

    pct_condonacion: Optional[int] = dc_field(default=None, repr=False)
    num_res_condonacion: Optional[str] = dc_field(default=None, repr=False)
    fecha_condonacion: Optional[date] = dc_field(default=None, repr=False)

    tipo_declaracion: Optional[str] = dc_field(default=None, repr=False)
    banco: Optional[str] = dc_field(default=None, repr=False)
    medio_pago: Optional[str] = dc_field(default=None, repr=False)
    fecha_presentacion: Optional[date] = dc_field(default=None, repr=False)

    extra: Mapping[int, object] = dc_field(default_factory=dict, repr=False)
    """
    Any SII Form 29 codes that do not have their own field go in `extra`.
    """

    _strict_codes: bool = dc_field(default=False, repr=False)
    """
    Consider unknown codes as invalid and reject them.

    The default is `False` because the SII Form 29 has a large number of codes and not all of them
    are known to this class. Also, the SII may add new codes at any time in the future.
    """

    CODE_FIELD_MAPPING: ClassVar[Mapping[int, Optional[str]]]
    """
    Map SII Form 29 numeric codes to their respective field names.

    If a numeric code is valid, but no field has been created for it, use `None` so that this class
    considers it as "known". Numeric codes that are not included here are considered unknown or
    invalid, even if they appear in the SII Form 29.
    """

    CODE_FIELD_MAPPING = {
        1: 'apellido_paterno_o_razon_social',  # "APELLIDO PATERNO O RAZÓN SOCIAL"
        2: 'apellido_materno',  # Apellido Materno
        3: 'contribuyente_rut',  # "N DE RUT"
        5: 'nombres',  # Nombres
        6: 'calle_direccion',  # "DIRECCION"
        7: 'folio',  # "FOLIO"
        8: 'comuna_direccion',  # "COMUNA"
        9: 'telefono',  # Teléfono
        15: 'periodo_tributario',  # "PERIODO TRIBUTARIO"
        20: None,  # Exportaciones | Monto Neto
        30: None,  # "PPM ART. 84, A) PERD. ART. 90"
        48: None,  # "RET. IMP. ÚNICO TRAB. ART. 74 N 1 LIR"
        55: 'correo_electronico',  # Correo Electrónico
        60: 'pct_condonacion',  # "PORCENTAJE CONDONACION TGR"
        62: None,  # "PPM NETO DET."
        77: None,  # "REMANENTE DE CRÉDITO FISC."
        89: None,  # "IMP. DETERM. IVA DETERM."
        91: 'total_a_pagar_en_plazo_legal',  # "TOTAL A PAGAR DENTRO DEL PLAZO"
        92: None,  # "REAJUSTES"
        93: None,  # "Intereses y multas"
        94: 'total_a_pagar_con_recargo',  # "Total a pagar con recargo"
        110: None,  # Boletas | Cantidad
        111: None,  # Boletas | Débitos
        115: None,  # "TASA PPM 1ra. CATEGORIA"
        142: None,  # "VENTAS Y/O SERV. EXENTOS O NO GRAVADOS"
        151: None,  # "RET, TASAS DE 10 % SOBRE LAS RENT."
        153: None,  # "RET, TASAS DE 10% o 20% SOBRE LAS RENT."
        314: 'representante_legal_rut',  # Rut Representante Legal
        315: 'fecha_presentacion',  # "FECHA TIMBRE CAJA"
        500: None,  # "CANTIDAD FACTURAS"
        501: None,  # "LIQUIDACION DE FACTURAS"
        502: None,  # "DÉBITOS FACTURAS EMITIDAS"
        503: None,  # "CANTIDAD FACTURAS EMITIDAS"
        504: None,  # "REMANENTE CREDITO MES ANTERIOR"
        509: None,  # "CANT. DCTOS. NOTAS DE CRÉDITOS EMITIDAS"
        510: None,  # "DÉBITOS  NOTAS DE CRÉDITOS EMITIDAS"
        511: None,  # "CRÉD. IVA POR DCTOS. ELECTRONICOS"
        512: None,  # "CANT. DE DCTOS. NOTAS DE DÉBITO EMIT."
        513: None,  # "NOTAS DE DÉBITOS EMITIDAS"
        514: None,  # IVA por documentos electrónicos recibidos | Sin derecho a Crédito
        515: None,  # Facturas de Compra recibidas c/ret. total y Fact. de Inicio emitida | Cantidad
        516: None,  # Facturas de Compra recibidas con retención parcial | Cantidad
        517: None,  # Facturas de Compra recibidas con retención parcial | Débitos
        519: None,  # "CANT. DE DCTOS. FACT. RECIB. DEL GIRO"
        520: None,  # "CRÉDITO REC. Y REINT./FACT. DEL GIRO"
        521: None,  # "MONTO NETO / INTERNAS AFECTAS"
        524: None,  # "CANT. FACT. ACTIVO FIJO"
        525: None,  # "CRÉD.  RECUP. Y REINT. FACT. ACTIVO FIJO"
        527: None,  # "CANT. NOTAS DE CRÉDITO RECIBIDAS"
        528: None,  # "CRÉDITO RECUP. Y REINT NOTAS DE CRÉD"
        531: None,  # "CANT. NOTAS DE DÉBITO RECIBIDAS"
        532: None,  # "NOTAS DE DÉBITO CRÉD, RECUP. Y REINT."
        534: None,  # Declaraciones de Ingreso (DIN) importaciones del giro | Cantidad
        535: None,  # Declaraciones de Ingreso (DIN) importaciones del giro | Créd., Recup. y Reint.
        536: None,  # Declaraciones de Ingreso (DIN) import. activo fijo | Cantidad
        537: None,  # "TOTAL CRÉDITOS"
        538: None,  # "TOTAL DÉBITOS"
        547: None,  # "TOTAL DETERMINADO"
        553: None,  # Declaraciones de Ingreso (DIN) import. activo fijo | Créd., Recup. y Reint.
        562: None,  # "MONTO SIN DER. A CRED. FISCAL"
        563: None,  # "BASE IMPONIBLE"
        564: None,  # "CANT. DOC. SIN DER. A CRED. FISCAL"
        584: None,  # "CANT.INT.EX.NO GRAV.SIN DER. CRED.FISCAL"
        585: None,  # Exportaciones | Cantidad
        586: None,  # "CANT. VTAS. Y/O SERV. PREST. INT. EXENT."
        587: None,  # Facturas de Compra recibidas c/ret. total y Fact. de Inicio emitida | Monto
        595: None,  # "SUB TOTAL IMP. DETERMINADO ANVERSO"
        596: None,  # "RETENCION CAMBIO DE SUJETO"
        601: None,  # Fax
        610: 'numero_direccion',  # Nº Dirección
        708: None,  # "CANT. NOTAS CRED. EMIT. VALES MAQ. IVA"
        709: None,  # "MONTO NOTAS CRED. EMIT. VALES MAQ. IVA."
        755: None,  # IVA Postergado
        756: None,  # Casillero (checkbox) "Postergación pago de IVA"
        761: None,  # "CANT. FACT. SUPERMERCADOS Y SIMILARES"
        762: None,  # "CRÉD. FACT. SUPERMERCADOS Y SIMILARES"
        763: None,  # "CANT. FACT. POR VENTA BIENES INMUEBLES"
        764: None,  # "DÉB. FACT. POR VENTA BIENES INMUEBLES"
        765: None,  # "CANT. FACT. ADQ. O CONSTR. B. INMUEBLES"
        766: None,  # "DÉB. FACT. ADQ. O CONSTR. B. INMUEBLES"
        795: None,  # "MONTO DE CONDONACION SII"
        915: 'fecha_condonacion',  # "Fecha de Vigencia de Condonacion"
        922: 'num_res_condonacion',  # "NUMERO RESOLUCION SII AUTO. CONDONACION"
        9906: None,  # "FECHA PRESENTACION DECL. PRIMITIVA"
    }

    def __post_init__(self) -> None:
        # -----Set Fields from Extra-----

        new_extra: MutableMapping[int, object] = {}

        for code, value in self.extra.items():
            field_name = self.get_field_name(code, strict=self._strict_codes)

            if field_name is None:
                # If there's no field for the code; leave it in `extra`.

                new_extra[code] = value
            else:
                # There's a field for the code; remove it from `extra`.

                current_field_value = getattr(self, field_name)
                if current_field_value is None:
                    # The current field's value is empty, so we set it.
                    object.__setattr__(self, field_name, value)
                else:
                    # The current field's value is not empty and we do not overwrite it. We give
                    # precedence to the current field's value because it may have been previously
                    # converted to a different data type (e.g. `periodo_tributario` has a code, but
                    # the code's value must be parsed and converted to an instance of
                    # `PeriodoTributario`).
                    pass

        object.__setattr__(self, 'extra', new_extra)

        # -----Validations-----

        validate_field_type(self, 'contribuyente_rut', Rut)
        validate_field_type(self, 'periodo_tributario', PeriodoTributario)
        validate_field_type(self, 'folio', int)
        validate_field_type(self, 'representante_legal_rut', (Rut, type(None)))
        validate_field_type(self, 'fecha_presentacion', (date, type(None)))

        if not all(isinstance(code, int) for code in self.extra):
            raise TypeError("All codes in 'extra' must be integers")

        # TODO: Validate the type of the other fields.

        # -----Warn About Unknown Codes-----

        if not self._strict_codes:
            unknown_codes = self.get_all_codes(strict=False) - self.get_all_codes(strict=True)
            if unknown_codes:
                logger.warning(
                    "%s(contribuyente_rut=%r, periodo_tributario=%r, folio=%r)"
                    " contains invalid or unknown SII Form 29 codes: %s.",
                    self.__class__.__name__,
                    self.contribuyente_rut,
                    self.periodo_tributario,
                    self.folio,
                    ', '.join(str(code) for code in sorted(unknown_codes)),
                )

    @classmethod
    def get_field_name(cls, code: int, strict: bool = True) -> Optional[str]:
        """
        Return the field name for the SII Form 29 code if a field name has been defined for the
        code. Return ``None`` if the code is known, but no field name is associated with it.

        :param code: SII Form 29 code.
        :param strict: Whether to consider unknown codes as invalid and raise an exception.

        :raises KeyError: If ``code`` is invalid and ``strict`` is ``True``.
        """
        if not isinstance(code, int):
            raise TypeError(f"An integer is required (got type '{code.__class__.__name__}')")

        try:
            return cls.CODE_FIELD_MAPPING[code]
        except KeyError as e:
            if strict:
                raise KeyError(f"Invalid or unknown SII Form 29 code: {code}") from e
            else:
                return None

    @property
    def natural_key(self) -> CteForm29NaturalKey:
        return CteForm29NaturalKey(
            contribuyente_rut=self.contribuyente_rut,
            periodo_tributario=self.periodo_tributario,
            folio=self.folio,
        )

    def get_all_codes(self, strict: Optional[bool] = None) -> Set[int]:
        """
        Return a set with all codes.

        :param strict: Whether to include unknown codes.
        """
        strict = self._strict_codes if strict is None else strict

        if strict:
            return set(self.CODE_FIELD_MAPPING)
        else:
            return {*self.CODE_FIELD_MAPPING, *self.extra}

    def as_codes_dict(
        self,
        include_none: bool = True,
        strict: Optional[bool] = None,
    ) -> Mapping[int, object]:
        """
        Return a dictionary of SII Form 29 codes and values. Fields that do not have a code are not
        included.

        :param include_none: Include codes that have an empty value (i.e. ``None``).
        :param strict: Whether to include unknown codes.
        """
        strict = self._strict_codes if strict is None else strict

        obj_dict = {code: self[code] for code in self.get_all_codes(strict=strict)}

        if not include_none:
            obj_dict = {code: value for code, value in obj_dict.items() if value is not None}

        return obj_dict

    def __getitem__(self, key: int) -> Any:
        """
        Return the value of the SII Form 29 code ``key``.
        """
        field_name = self.get_field_name(key, strict=self._strict_codes)

        if field_name is None:
            # Field is valid, but no field name has been associated with it.
            return self.extra.get(key)
        else:
            # Field is valid and it has a field name.
            return getattr(self, field_name)

    def __iter__(self) -> Iterator:
        for dc_field_obj in dataclasses.fields(self):
            if not dc_field_obj.name.startswith('_'):  # Exclude private fields.
                yield (dc_field_obj.name, getattr(self, dc_field_obj.name))


def validate_field_type(
    obj: object,
    field_name: str,
    valid_types: Union[Type[Any], Tuple[Type[Any], ...]],
) -> None:
    if isinstance(valid_types, type):
        valid_types = (valid_types,)

    value = getattr(obj, field_name)
    if not isinstance(value, valid_types):
        raise TypeError(
            f"'{field_name}' must be an instance of"
            f" {', '.join(t.__name__ for t in valid_types)},"
            f" not '{value.__class__.__name__}'"
        )
