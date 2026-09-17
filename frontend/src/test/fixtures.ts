// Generated from the bridge and unchanged M0.9 kernel; test data only.
import type { HistoricalManifest, HistoricalExecution } from '../instrument/types'
export const manifestFixture: HistoricalManifest = {
  "cell": {
    "bank_label": "Dodecamorium",
    "cell_label": "Cell IV",
    "pinax": 4,
    "printed_page": "83",
    "syntagma": 1
  },
  "content_digest": "92644fc2b90712ec6dce49f66df3cb60a00702822339891d4697d1baf796ba15",
  "critical_edition_carrier": {
    "carrier_id": "S1.P4.CRITICAL_EDITION.FRAGMENT01",
    "classification": "H1",
    "edition_id": "neo-arca-critical-edition/1",
    "editorial_pairing": {
      "classification": "H1",
      "note": "Vperm01 and Rperm03 are separately verified selections; their pairing and carrier layout are editorial reconstruction, not a recovered complete historical column."
    },
    "label": "Pinax IV critical-edition extract",
    "pitch_source": {
      "content": {
        "rows": {
          "altus": [
            8,
            7,
            5,
            7,
            7,
            7
          ],
          "bassus": [
            8,
            5,
            8,
            7,
            3,
            3
          ],
          "cantus": [
            5,
            5,
            3,
            2,
            3,
            3
          ],
          "tenor": [
            3,
            2,
            3,
            4,
            5,
            5
          ]
        }
      },
      "immutable_record": "syntagma1_pinax04_stropha1_vperm01_printed_p83",
      "provenance_paths": [
        "S1.P4.STROPHA1.VPERM01.CANTUS.N01",
        "S1.P4.STROPHA1.VPERM01.CANTUS.N02",
        "S1.P4.STROPHA1.VPERM01.CANTUS.N03",
        "S1.P4.STROPHA1.VPERM01.CANTUS.N04",
        "S1.P4.STROPHA1.VPERM01.CANTUS.N05",
        "S1.P4.STROPHA1.VPERM01.CANTUS.N06",
        "S1.P4.STROPHA1.VPERM01.ALTUS.N01",
        "S1.P4.STROPHA1.VPERM01.ALTUS.N02",
        "S1.P4.STROPHA1.VPERM01.ALTUS.N03",
        "S1.P4.STROPHA1.VPERM01.ALTUS.N04",
        "S1.P4.STROPHA1.VPERM01.ALTUS.N05",
        "S1.P4.STROPHA1.VPERM01.ALTUS.N06",
        "S1.P4.STROPHA1.VPERM01.TENOR.N01",
        "S1.P4.STROPHA1.VPERM01.TENOR.N02",
        "S1.P4.STROPHA1.VPERM01.TENOR.N03",
        "S1.P4.STROPHA1.VPERM01.TENOR.N04",
        "S1.P4.STROPHA1.VPERM01.TENOR.N05",
        "S1.P4.STROPHA1.VPERM01.TENOR.N06",
        "S1.P4.STROPHA1.VPERM01.BASSUS.N01",
        "S1.P4.STROPHA1.VPERM01.BASSUS.N02",
        "S1.P4.STROPHA1.VPERM01.BASSUS.N03",
        "S1.P4.STROPHA1.VPERM01.BASSUS.N04",
        "S1.P4.STROPHA1.VPERM01.BASSUS.N05",
        "S1.P4.STROPHA1.VPERM01.BASSUS.N06"
      ],
      "source_column_id": "S1.P4.STROPHA1.VPERM01"
    },
    "rhythm_source": {
      "content": {
        "glyphs": [
          "minim",
          "minim",
          "minim",
          "minim",
          "semibreve",
          "semibreve"
        ],
        "glyphs_classification": "H0",
        "relative_minim_units": [
          1,
          1,
          1,
          1,
          2,
          2
        ],
        "relative_minim_units_classification": "derived project normalization"
      },
      "immutable_record": "syntagma1_pinax04_rhythm_duple_rperm03_printed_p83",
      "provenance_paths": [
        "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N01",
        "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N02",
        "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N03",
        "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N04",
        "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N05",
        "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N06"
      ],
      "source_column_id": "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03"
    }
  },
  "format": "neo-arca-mechanica-manifest/v2",
  "limits": [
    "One editorially selected fragment; no selectable untranscribed bands.",
    "Symbolic content is source-backed; its software representation is modern.",
    "No octave, register, MIDI pitch, BPM, beat semantics, ficta or SATB repair."
  ],
  "manifest_id": "m1.2.1r.pinax04.fragment01",
  "physical_reconstruction": {
    "classification": "H1",
    "note": "Carrier face, workstation capacity and six-event inspection mechanism are reconstruction, not historical transverse reading."
  },
  "title": "PINAX IV. Iambica Euripedaea penultima longa.",
  "tone": {
    "degree_to_pitch_class": {
      "1": "G",
      "2": "A",
      "3": "Bb",
      "4": "C",
      "5": "D",
      "6": "Eb",
      "7": "F#",
      "8": "G"
    },
    "known_conflict": "The printed-p.51 table conflicts with the engraved tone table. This edition retains the M0.9 p.51 witness policy; it does not claim a preferred general operating authority.",
    "name": "Hypodorius",
    "number": 2,
    "operating_policy_classification": "H1",
    "provenance_class": "H0-V",
    "record": "mensa_tonographica_tone02_hypodorius_printed_p51",
    "system": "mollis",
    "witness": "printed p.51 Mensa Tonographica",
    "witness_classification": "H0"
  }
}
export const executionFixture: HistoricalExecution = {
  "format": "neo-arca-mechanica-execution/v2",
  "fragment": {
    "canonical": true,
    "description": "Pinax-IV historical fragment",
    "edition_policy": "PRINT_1650",
    "events": [
      {
        "duration_minim_units": 1,
        "duration_symbol": "minim",
        "index": 1,
        "offset_minim_units": 0,
        "rhythm_provenance": {
          "cell": "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N01"
        },
        "voices": {
          "altus": {
            "degree": 8,
            "pitch_class": "G",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE08",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.ALTUS.N01"
            }
          },
          "bassus": {
            "degree": 8,
            "pitch_class": "G",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE08",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.BASSUS.N01"
            }
          },
          "cantus": {
            "degree": 5,
            "pitch_class": "D",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE05",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.CANTUS.N01"
            }
          },
          "tenor": {
            "degree": 3,
            "pitch_class": "Bb",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE03",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.TENOR.N01"
            }
          }
        }
      },
      {
        "duration_minim_units": 1,
        "duration_symbol": "minim",
        "index": 2,
        "offset_minim_units": 1,
        "rhythm_provenance": {
          "cell": "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N02"
        },
        "voices": {
          "altus": {
            "degree": 7,
            "pitch_class": "F#",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE07",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.ALTUS.N02"
            }
          },
          "bassus": {
            "degree": 5,
            "pitch_class": "D",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE05",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.BASSUS.N02"
            }
          },
          "cantus": {
            "degree": 5,
            "pitch_class": "D",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE05",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.CANTUS.N02"
            }
          },
          "tenor": {
            "degree": 2,
            "pitch_class": "A",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE02",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.TENOR.N02"
            }
          }
        }
      },
      {
        "duration_minim_units": 1,
        "duration_symbol": "minim",
        "index": 3,
        "offset_minim_units": 2,
        "rhythm_provenance": {
          "cell": "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N03"
        },
        "voices": {
          "altus": {
            "degree": 5,
            "pitch_class": "D",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE05",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.ALTUS.N03"
            }
          },
          "bassus": {
            "degree": 8,
            "pitch_class": "G",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE08",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.BASSUS.N03"
            }
          },
          "cantus": {
            "degree": 3,
            "pitch_class": "Bb",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE03",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.CANTUS.N03"
            }
          },
          "tenor": {
            "degree": 3,
            "pitch_class": "Bb",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE03",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.TENOR.N03"
            }
          }
        }
      },
      {
        "duration_minim_units": 1,
        "duration_symbol": "minim",
        "index": 4,
        "offset_minim_units": 3,
        "rhythm_provenance": {
          "cell": "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N04"
        },
        "voices": {
          "altus": {
            "degree": 7,
            "pitch_class": "F#",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE07",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.ALTUS.N04"
            }
          },
          "bassus": {
            "degree": 7,
            "pitch_class": "F#",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE07",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.BASSUS.N04"
            }
          },
          "cantus": {
            "degree": 2,
            "pitch_class": "A",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE02",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.CANTUS.N04"
            }
          },
          "tenor": {
            "degree": 4,
            "pitch_class": "C",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE04",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.TENOR.N04"
            }
          }
        }
      },
      {
        "duration_minim_units": 2,
        "duration_symbol": "semibreve",
        "index": 5,
        "offset_minim_units": 4,
        "rhythm_provenance": {
          "cell": "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N05"
        },
        "voices": {
          "altus": {
            "degree": 7,
            "pitch_class": "F#",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE07",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.ALTUS.N05"
            }
          },
          "bassus": {
            "degree": 3,
            "pitch_class": "Bb",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE03",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.BASSUS.N05"
            }
          },
          "cantus": {
            "degree": 3,
            "pitch_class": "Bb",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE03",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.CANTUS.N05"
            }
          },
          "tenor": {
            "degree": 5,
            "pitch_class": "D",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE05",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.TENOR.N05"
            }
          }
        }
      },
      {
        "duration_minim_units": 2,
        "duration_symbol": "semibreve",
        "index": 6,
        "offset_minim_units": 6,
        "rhythm_provenance": {
          "cell": "S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03.N06"
        },
        "voices": {
          "altus": {
            "degree": 7,
            "pitch_class": "F#",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE07",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.ALTUS.N06"
            }
          },
          "bassus": {
            "degree": 3,
            "pitch_class": "Bb",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE03",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.BASSUS.N06"
            }
          },
          "cantus": {
            "degree": 3,
            "pitch_class": "Bb",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE03",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.CANTUS.N06"
            }
          },
          "tenor": {
            "degree": 5,
            "pitch_class": "D",
            "provenance": {
              "tone_cell": "MENSA.P51.TONE02.DEGREE05",
              "vperm_cell": "S1.P4.STROPHA1.VPERM01.TENOR.N06"
            }
          }
        }
      }
    ],
    "explicitly_not_claimed": [
      "absolute octave/register placement",
      "modern MIDI note numbers",
      "absolute tempo or BPM",
      "modern beat-unit semantics",
      "phrase-level musica-ficta beyond the selected printed-p.51 tone witness",
      "identity with Kircher's prose Ave maris stella worked example"
    ],
    "format": "neo-arca-historica-symbolic/v1",
    "provenance": {
      "components": {
        "pitch_permutation": {
          "record": "syntagma1_pinax04_stropha1_vperm01_printed_p83",
          "witness_ids": [
            "BSB_MUNICH_2_MUS_TH_264_2_1650",
            "IA_EPFL_CHEPFL_LIPR_AXC19_02_1650"
          ]
        },
        "rhythm": {
          "record": "syntagma1_pinax04_rhythm_duple_rperm03_printed_p83",
          "witness_ids": [
            "BSB_MUNICH_2_MUS_TH_264_2_1650",
            "IA_EPFL_CHEPFL_LIPR_AXC19_02_1650",
            "BNF_GALLICA_RES_F_142_T2_1650"
          ]
        },
        "tone_lookup": {
          "record": "mensa_tonographica_tone02_hypodorius_printed_p51",
          "witness_ids": [
            "BSB_MUNICH_2_MUS_TH_264_2_1650",
            "IA_EPFL_CHEPFL_LIPR_AXC19_02_1650"
          ]
        }
      },
      "transcription_protocol": "docs/HISTORICAL_DATA_TRANSCRIPTION_SPEC.md",
      "witnesses": [
        {
          "id": "BNF_GALLICA_RES_F_142_T2_1650",
          "independence_key": "BNF-RES-F-142",
          "institution": "Bibliothèque nationale de France, département Musique / Gallica",
          "record": "https://gallica.bnf.fr/ark:/12148/bpt6k12802862"
        },
        {
          "id": "BSB_MUNICH_2_MUS_TH_264_2_1650",
          "independence_key": "BSB-2-MUS.TH.264-2",
          "institution": "Bayerische Staatsbibliothek München",
          "record": "https://archive.org/details/bub_gb_97xCAAAAcAAJ"
        },
        {
          "id": "IA_EPFL_CHEPFL_LIPR_AXC19_02_1650",
          "independence_key": "EPFL-PLUME-1455",
          "institution": "EPFL Library / Internet Archive",
          "record": "https://archive.org/details/chepfl-lipr-AXC19_02"
        }
      ]
    },
    "selection": {
      "pinax": 4,
      "rperm": 3,
      "stropha": 1,
      "syntagma": 1,
      "system": "mollis",
      "tone": 2,
      "tone_name": "Hypodorius",
      "tone_witness": "printed p.51 Mensa Tonographica",
      "vperm": 1
    },
    "status": "verified-historical-fragment",
    "time_unit": "relative minim",
    "total_duration_minim_units": 8
  },
  "reading": {
    "carrier_instance": {
      "carrier_id": "S1.P4.CRITICAL_EDITION.FRAGMENT01",
      "edition_id": "neo-arca-critical-edition/1",
      "instance_id": "carrier-pinax04-fragment-1",
      "location": "workspace"
    },
    "classification": "H0-backed content through H1 critical-edition carrier",
    "content_digest": "92644fc2b90712ec6dce49f66df3cb60a00702822339891d4697d1baf796ba15",
    "manifest_id": "m1.2.1r.pinax04.fragment01",
    "tone": {
      "number": 2,
      "witness": "printed p.51 Mensa Tonographica"
    }
  },
  "request_fingerprint": "51441857d720847554c1800ad83542d048079267c61841d8c4ef726c3e6f4e7c"
}
