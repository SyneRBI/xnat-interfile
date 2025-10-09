/*
 * xnat-interfile-plugin:
 * XNAT http://www.xnat.org
 * Copyright (c) 2022, Physikalisch-Technische Bundesanstalt
 * All Rights Reserved
 *
 * Released under Apache 2.0
 */

package org.nrg.xnat.interfile;

import org.nrg.framework.annotations.XnatDataModel;
import org.nrg.framework.annotations.XnatPlugin;
import org.nrg.xdat.bean.InterfilePetlmscandataBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;

@XnatPlugin(value = "interfilePlugin", name = "XNAT 1.8 Interfile plugin",
            dataModels = {@XnatDataModel(value = InterfilePetlmscandataBean.SCHEMA_ELEMENT_NAME,
                                         singular = "PET listmode data",
                                         plural = "PET listmode data",
                                         code = "INTERFILELM")})
public class InterfileXnatPlugin {
}
